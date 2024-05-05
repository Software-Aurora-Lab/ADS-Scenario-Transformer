import math
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple, Set
from lanelet2.core import LaneletMap
from lanelet2.projection import MGRSProjector
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles, PerceptionObstacle
from modules.common.proto.geometry_pb2 import PointENU, Point3D
from openscenario_msgs import Story, ScenarioObject, Position, Rule, SpeedActionDynamics, TransitionDynamics, Event, Condition, Act, Vehicle
from ads_scenario_transformer.transformer import Transformer
from ads_scenario_transformer.transformer.pointenu_transformer import PointENUTransformer, PointENUTransformerConfiguration
from ads_scenario_transformer.builder.storyboard.story_builder import StoryBuilder
from ads_scenario_transformer.builder.storyboard.act_builder import ActBuilder
from ads_scenario_transformer.builder.storyboard.actors_builder import ActorsBuilder
from ads_scenario_transformer.builder.storyboard.maneuver_group_builder import ManeuverGroupBuilder
from ads_scenario_transformer.builder.storyboard.maneuver_builder import ManeuverBuilder
from ads_scenario_transformer.builder.storyboard.event_builder import EventBuilder
from ads_scenario_transformer.builder.storyboard.private_action_builder import PrivateActionBuilder
from ads_scenario_transformer.builder.storyboard.global_action_builder import GlobalActionBuilder
from ads_scenario_transformer.builder.storyboard.condition_builder import ConditionBuilder
from ads_scenario_transformer.builder.storyboard.trigger_builder import StartTriggerBuilder
from ads_scenario_transformer.builder.entities_builder import EntitiesBuilder, ASTEntity, ASTEntityType


@dataclass
class ObstaclesTransformerConfiguration:
    sceanrio_start_timestamp: float
    lanelet_map: LaneletMap
    projector: MGRSProjector
    waypoint_frequency_in_sec: Optional[
        float]  # None = direction detection, 0 = all waypoints, others = input frequency, Average frequency of the PerceptionObstacles channel is 0.04s to 0.05s. If you set lower than 0.04s, the obstacles will add all waypoints.
    direction_change_detection_threshold: float = 60


@dataclass
class ObstaclesTransformerResult:
    entities_with_id: List[Tuple[ASTEntity, ScenarioObject]]
    stories: List[Story]


class ObstaclesTransformer(Transformer):
    configuration: ObstaclesTransformerConfiguration

    Source = List[PerceptionObstacles]
    Target = ObstaclesTransformerResult

    def __init__(self, configuration: ObstaclesTransformerConfiguration):
        self.configuration = configuration

    def transform(
            self,
            source: List[PerceptionObstacles]) -> ObstaclesTransformerResult:

        if source[0].error_code:
            return ObstaclesTransformerResult(entities_with_id=[], stories=[])

        entities_with_id = self.get_obstacles(source)
        grouped_obstacles = self.group_obstacles(obstacles=source)

        stories = []
        for id, obstacles in grouped_obstacles.items():
            target_object = self.find_scenario_object(
                id=id, entities_with_id=entities_with_id)

            if not target_object:
                continue

            start = obstacles[0]
            start_position = self.transform_coordinate_value(
                position=start.position, scenario_object=target_object)

            if not start_position:
                raise ValueError(
                    "start poisiion of the obstacle cannot be projected")

            simulation_start_condition = ConditionBuilder.simulation_time_condition(
                rule=Rule.GREATER_THAN, value_in_sec=0)

            locating_event = self.create_locating_obstacle_event(
                start_condition=simulation_start_condition,
                position=start_position,
                entity_name=target_object.name)

            events = [locating_event]
            if self.is_obstacle_moved(obstacles):

                start_moving_time = self.obstacle_start_moving_time(obstacles)
                start_condition = ConditionBuilder.ego_start_moving_condition(
                    delay=start_moving_time)

                routing_positions = []
                for idx in self.obstacle_routing_indices(obstacles):
                    position = self.transform_coordinate_value(
                        obstacles[idx].position, scenario_object=target_object)
                    if position:
                        routing_positions.append(position)
                    else:
                        print(
                            f"Warning: Position in {target_object.name} route cannot be projected, because it is not projected in Lanelet. It will not applied in result scenario"
                        )

                if routing_positions:
                    routing_event = self.create_routing_event(
                        start_condition=start_condition,
                        routing_positions=routing_positions,
                        max_velocity=self.max_velocity_meter_per_sec(
                            obstacles=obstacles),
                        entity_name=target_object.name)
                    events.append(routing_event)

            act = self.wrap_events_to_act(
                events=events,
                start_condition=simulation_start_condition,
                entity_names=[target_object.name])
            story_builder = StoryBuilder(name=f"{target_object.name} Story")
            story_builder.make_acts(acts=[act])
            stories.append(story_builder.get_result())

        return ObstaclesTransformerResult(entities_with_id=entities_with_id,
                                          stories=stories)

    # helper functions

    def get_obstacles(
        self, obstacles: List[PerceptionObstacles]
    ) -> List[Tuple[ASTEntity, ScenarioObject]]:

        uniq_obstacles = {}
        for obstacle in obstacles:
            for ob in obstacle.perception_obstacle:
                if ob.id not in uniq_obstacles:
                    entity_type = None
                    if ob.type == 3:
                        entity_type = ASTEntityType.PEDESTRIAN
                    elif ob.type == 4:
                        entity_type = ASTEntityType.BICYCLE
                    elif ob.type == 5:
                        entity_type = ASTEntityType.CAR
                    else:
                        continue

                    ast_entity = ASTEntity(entity_type=entity_type,
                                           use_default_scenario_object=False,
                                           embedding_id=ob.id,
                                           length=ob.length,
                                           height=ob.height,
                                           width=ob.width)
                    uniq_obstacles[ob.id] = ast_entity

        entities_builder = EntitiesBuilder()
        for id, ast_entity in uniq_obstacles.items():
            entities_builder.add_entity(ast_entity=ast_entity)

        return entities_builder.scenario_objects

    def create_locating_obstacle_event(self, start_condition: Condition,
                                       position: Position,
                                       entity_name: str) -> Event:
        event_builder = EventBuilder(start_conditions=[start_condition])
        global_action_builder = GlobalActionBuilder()
        global_action_builder.make_add_entity_action(position=position,
                                                     entity_name=entity_name)
        global_action = global_action_builder.get_result()
        event_builder.add_global_action(
            name=f"Locate {entity_name} on the road",
            global_action=global_action)

        # If you don't set its speed to 0, obstacles start running ignoring specified condition.
        private_action_builder = PrivateActionBuilder()
        private_action_builder.make_absolute_speed_action(
            speed_action_dynamics=SpeedActionDynamics(
                dynamicsDimension=TransitionDynamics.DynamicsDimension.TIME,
                dynamicsShape=TransitionDynamics.DynamicsShape.STEP,
                value=0),
            value=0)
        speed_action = private_action_builder.get_result()
        event_builder.add_private_action(
            name=f"Stop {entity_name} at starting point",
            private_action=speed_action)

        return event_builder.get_result()

    def create_routing_event(self, start_condition: Condition,
                             routing_positions: List[Position],
                             max_velocity: float, entity_name: str) -> Event:
        event_builder = EventBuilder(start_conditions=[start_condition])

        private_action_builder = PrivateActionBuilder()
        private_action_builder.make_absolute_speed_action(
            speed_action_dynamics=SpeedActionDynamics(
                dynamicsDimension=TransitionDynamics.DynamicsDimension.TIME,
                dynamicsShape=TransitionDynamics.DynamicsShape.STEP,
                value=0),
            value=max_velocity)
        speed_action = private_action_builder.get_result()
        event_builder.add_private_action(name=f"Speed of {entity_name}",
                                         private_action=speed_action)

        private_action_builder.make_routing_action(positions=routing_positions,
                                                   name="")
        private_action = private_action_builder.get_result()
        event_builder.add_private_action(name=f"Route {entity_name}",
                                         private_action=private_action)
        return event_builder.get_result()

    def wrap_events_to_act(self, events: List[Event],
                           start_condition: Condition,
                           entity_names: List[str]) -> Act:
        maneuver_builder = ManeuverBuilder()
        maneuver_builder.make_events(events=events)

        maneuver_group_builder = ManeuverGroupBuilder()
        maneuver_group_builder.make_maneuvers(
            maneuvers=[maneuver_builder.get_result()])

        actors_builder = ActorsBuilder()
        for entity_name in entity_names:
            actors_builder.add_entity_ref(scenario_object_name=entity_name)

        maneuver_group_builder.make_actors(actors=actors_builder.get_result())
        maneuver_group = maneuver_group_builder.get_result()
        strat_trigger = StartTriggerBuilder()
        strat_trigger.make_condition_group(conditions=[start_condition])
        act_builder = ActBuilder(name="")
        act_builder.make_maneuver_groups(maneuver_groups=[maneuver_group])
        act_builder.make_start_trigger(trigger=strat_trigger.get_result())
        return act_builder.get_result()

    def is_obstacle_moved(self, obstacles: List[PerceptionObstacle]) -> bool:
        return self.max_velocity_meter_per_sec(obstacles=obstacles) != 0.0

    def group_obstacles(
        self, obstacles: List[PerceptionObstacles]
    ) -> Dict[str, List[PerceptionObstacles]]:
        grouped_obstacles = {}
        for perception_obstacles in obstacles:
            for obstacle in perception_obstacles.perception_obstacle:

                if obstacle.id not in grouped_obstacles:
                    grouped_obstacles[obstacle.id] = []
                grouped_obstacles[obstacle.id].append(obstacle)
        return grouped_obstacles

    def obstacle_start_moving_idx(self,
                                  obstacles: List[PerceptionObstacle]) -> int:
        obstacle_start_moving_idx = 0
        for i, obstacle in enumerate(obstacles):
            velocity = self.calculate_velocity_meter_per_sec(obstacle.velocity)
            if velocity > 0:
                obstacle_start_moving_idx = i
                break

        return obstacle_start_moving_idx

    def obstacle_end_moving_idx(self,
                                obstacles: List[PerceptionObstacle]) -> int:
        obstacle_end_moving_idx = len(obstacles) - 1
        for i, obstacle in enumerate(reversed(obstacles)):
            velocity = self.calculate_velocity_meter_per_sec(obstacle.velocity)
            if velocity > 0:
                obstacle_end_moving_idx = len(obstacles) - 1 - i
                break

        return obstacle_end_moving_idx

    def obstacle_start_moving_time(
            self, obstacles: List[PerceptionObstacle]) -> float:
        obstacle_start_moving_idx = self.obstacle_start_moving_idx(obstacles)

        return max(
            obstacles[obstacle_start_moving_idx].timestamp -
            self.configuration.sceanrio_start_timestamp, 0)

    def obstacle_routing_indices(
            self, obstacles: List[PerceptionObstacle]) -> List[int]:
        frequency = self.configuration.waypoint_frequency_in_sec

        result = []
        if frequency is None:
            start_moving_idx = self.obstacle_start_moving_idx(obstacles)
            end_moving_idx = self.obstacle_end_moving_idx(obstacles)

            direction_changed_indices = self.obstacle_direction_changed_indices(
                obstacles)
            result = [start_moving_idx] + [
                idx
                for idx in direction_changed_indices if idx > start_moving_idx
            ] + [end_moving_idx]
        else:
            if obstacles:
                start_timestamp = obstacles[0].timestamp
                result.append(0)
                for idx, obstacle in enumerate(obstacles[1:]):
                    if frequency < obstacle.timestamp - start_timestamp:
                        result.append(idx + 1)
                        start_timestamp = obstacle.timestamp

        return result

    def normalize_radians(self, angle):
        return angle % (2 * math.pi)

    def obstacle_direction_changed_indices(
            self, obstacles: List[PerceptionObstacle]) -> List[int]:
        assert 0 <= self.configuration.direction_change_detection_threshold <= 360

        routing_indices = []
        for idx, (prev_obstacle, next_obstacle) in enumerate(
                zip(obstacles[:-1], obstacles[1:])):
            prev_degree = math.degrees(
                self.normalize_radians(prev_obstacle.theta))
            next_degree = math.degrees(
                self.normalize_radians(next_obstacle.theta))

            if abs(prev_degree - next_degree
                   ) > self.configuration.direction_change_detection_threshold:
                routing_indices.append(idx)

        return routing_indices

    def calculate_velocity_meter_per_sec(self, velocity) -> float:
        x, y, z = velocity.x, velocity.y, velocity.z
        return math.sqrt(x**2 + y**2)

    def max_velocity_meter_per_sec(
            self, obstacles: List[PerceptionObstacle]) -> float:
        return max([
            self.calculate_velocity_meter_per_sec(obstacle.velocity)
            for obstacle in obstacles
        ])

    def find_scenario_object(
        self, id: str, entities_with_id: List[Tuple[ASTEntity, ScenarioObject]]
    ) -> Optional[ScenarioObject]:

        for (meta, scenario_object) in entities_with_id:
            if meta.embedding_id == id:
                return scenario_object
        return None

    def transform_coordinate_value(
            self, position: Point3D,
            scenario_object: ScenarioObject) -> Optional[Position]:

        point = PointENU(x=position.x, y=position.y, z=0)
        transformer = PointENUTransformer(
            configuration=PointENUTransformerConfiguration(
                supported_position=PointENUTransformer.SupportedPosition.Lane,
                lanelet_map=self.configuration.lanelet_map,
                projector=self.configuration.projector,
                lanelet_subtypes=self.available_lane_subtypes(
                    scenario_object)))

        position = transformer.transform(source=(point, 0.0))
        return position

    def available_lane_subtypes(self,
                                scenario_object: ScenarioObject) -> Set[str]:

        if scenario_object.entityObject.HasField("pedestrian"):
            return ASTEntityType.PEDESTRIAN.available_lanelet_subtype()
        elif scenario_object.entityObject.HasField("vehicle"):
            if scenario_object.entityObject.vehicle.vehicleCategory == Vehicle.Category.BICYCLE:
                return ASTEntityType.BICYCLE.available_lanelet_subtype()
            elif scenario_object.entityObject.vehicle.vehicleCategory == Vehicle.Category.CAR:
                return ASTEntityType.CAR.available_lanelet_subtype()
        return set()
