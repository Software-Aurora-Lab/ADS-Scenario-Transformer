from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
import lanelet2
from lanelet2.core import LaneletMap
from lanelet2.projection import MGRSProjector
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles, PerceptionObstacle
from modules.common.proto.geometry_pb2 import PointENU, Point3D
from openscenario_msgs import Story, ScenarioObject, Position, Waypoint, RouteStrategy, Entities, Rule
from scenario_transformer.transformer import Transformer
from scenario_transformer.transformer.pointenu_transformer import PointENUTransformer, PointENUTransformerConfiguration
from scenario_transformer.builder.storyboard.story_builder import StoryBuilder
from scenario_transformer.builder.storyboard.act_builder import ActBuilder
from scenario_transformer.builder.storyboard.actors_builder import ActorsBuilder
from scenario_transformer.builder.storyboard.maneuver_group_builder import ManeuverGroupBuilder
from scenario_transformer.builder.storyboard.maneuver_builder import ManeuverBuilder
from scenario_transformer.builder.storyboard.event_builder import EventBuilder
from scenario_transformer.builder.storyboard.private_action_builder import PrivateActionBuilder
from scenario_transformer.builder.storyboard.routing_action_builder import RoutingActionBuilder
from scenario_transformer.builder.storyboard.condition_builder import ConditionBuilder
from scenario_transformer.builder.storyboard.trigger_builder import StartTriggerBuilder
from scenario_transformer.builder.entities_builder import EntityType, EntityMeta


@dataclass
class ObstaclesTransformerConfiguration:
    scenario_objects: List[Tuple[EntityMeta, ScenarioObject]]
    sceanrio_start_timestamp: float
    lanelet_map: LaneletMap
    projector: lanelet2.projection.MGRSProjector


class ObstaclesTransformer(Transformer):

    configuration: ObstaclesTransformerConfiguration

    Source = List[PerceptionObstacles]
    Target = List[Story]

    def __init__(self, configuration: ObstaclesTransformerConfiguration):
        self.configuration = configuration

    def transform(self,
                  source: List[PerceptionObstacles]) -> List[Story]:

        if source[0].error_code:
            return []

        grouped_obstacles = self.group_obstacles(obstacles=source)

        stories = []
        for id, obstacles in grouped_obstacles.items():
            
            target_object = next(scenario_object for (meta, scenario_object) in self.configuration.scenario_objects if meta.embedding_id == id)
            
            if not target_object:
                continue

            start = obstacles[0]
            mid = obstacles[len(obstacles) // 2]
            end = obstacles[-1]

            simulation_start_condition = ConditionBuilder.simulation_time_condition(
                rule=Rule.GREATER_THAN, value_in_sec=0)

            start_moving_time = self.obstacle_start_moving_time(obstacles)
            start_condition = ConditionBuilder.simulation_time_condition(
                rule=Rule.GREATER_THAN, value_in_sec=start_moving_time)
            event_builder = EventBuilder(start_conditions=[start_condition])
            start_position = self.transform_coordinate_value(
                position=start.position)

            private_action_builder = PrivateActionBuilder()
            private_action_builder.make_teleport_action(position=start_position)
            teleport_action = private_action_builder.get_result()
            event_builder.add_private_action(name="Locate an obstacle", private_action=teleport_action)
            
            
            if start.position != end.position:
                mid_position = self.transform_coordinate_value(
                    position=mid.position)
                end_position = self.transform_coordinate_value(
                    position=end.position)
                
                private_action_builder.make_routing_action(positions=[mid_position, end_position], name="")
                private_action = private_action_builder.get_result()
                event_builder.add_private_action(name="Route an obstacle", 
                                                 private_action=private_action)
                
            event = event_builder.get_result()
            maneuver_builder = ManeuverBuilder()
            maneuver_builder.add_event(event=event)

            maneuver_group_builder = ManeuverGroupBuilder()
            maneuver_group_builder.make_maneuvers(
                maneuvers=[maneuver_builder.get_result()])
            actors_builder = ActorsBuilder()
            actors_builder.add_entity_ref(scenario_object_name=target_object.name)

            maneuver_group_builder.make_actors(actors=actors_builder.get_result())
            maneuver_group = maneuver_group_builder.get_result()
            strat_trigger = StartTriggerBuilder()
            strat_trigger.make_condition_group(conditions=[simulation_start_condition])
            act_builder = ActBuilder(name="")
            act_builder.make_maneuver_groups(maneuver_groups=[maneuver_group])
            act_builder.make_start_trigger(trigger=strat_trigger.get_result())
            act = act_builder.get_result()
            story_builder = StoryBuilder(name=f"Run {target_object.name}")
            story_builder.make_acts(acts=[act])
            stories.append(story_builder.get_result())

        return stories

    # helper functions
    
    def group_obstacles(self, 
                        obstacles: List[PerceptionObstacles]) -> Dict[str, List[PerceptionObstacles]]:
        grouped_obstacles = {}
        for perception_obstacles in obstacles:
            for obstacle in perception_obstacles.perception_obstacle:

                if obstacle.id not in grouped_obstacles:
                    grouped_obstacles[obstacle.id] = []
                grouped_obstacles[obstacle.id].append(obstacle)
        return grouped_obstacles

    def obstacle_start_moving_time(self, obstacles: List[PerceptionObstacle]) -> float:
        obstacle_start_moving_idx = 0
        for idx, (ob_prev, ob_cur) in enumerate(zip(obstacles[:-1], obstacles[1:])):
            if ob_prev.position != ob_cur.position:
                obstacle_start_moving_idx = idx
                break

        return max(obstacles[obstacle_start_moving_idx].timestamp - self.configuration.sceanrio_start_timestamp, 0)

    def transform_coordinate_value(self, position: Point3D) -> Position:
        point = PointENU(x=position.x, y=position.y, z=0)
        laneType = PointENUTransformer.SupportedPosition.Lane
        transformer = PointENUTransformer(
            configuration=PointENUTransformerConfiguration(
                supported_position=laneType,
                lanelet_map=self.configuration.lanelet_map,
                projector=self.configuration.projector))

        return transformer.transform(source=(point, 0.0))