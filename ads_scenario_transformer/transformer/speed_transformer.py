import math
from enum import Enum
from typing import List
from dataclasses import dataclass
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles, PerceptionObstacle
from modules.common.proto.geometry_pb2 import Point3D
from openscenario_msgs import Story, Event, Condition, Act, Rule, SpeedActionDynamics, TransitionDynamics
from ads_scenario_transformer.transformer import Transformer
from ads_scenario_transformer.builder.storyboard.act_builder import ActBuilder
from ads_scenario_transformer.builder.storyboard.actors_builder import ActorsBuilder
from ads_scenario_transformer.builder.storyboard.maneuver_group_builder import ManeuverGroupBuilder
from ads_scenario_transformer.builder.storyboard.maneuver_builder import ManeuverBuilder
from ads_scenario_transformer.builder.storyboard.event_builder import EventBuilder
from ads_scenario_transformer.builder.storyboard.private_action_builder import PrivateActionBuilder
from ads_scenario_transformer.builder.storyboard.condition_builder import ConditionBuilder
from ads_scenario_transformer.builder.storyboard.trigger_builder import StartTriggerBuilder


@dataclass
class SpeedTransformerConfiguration:
    entity_name: str


@dataclass
class SpeedTransformerResult:
    act: Act


class SpeedState(Enum):
    INCREASING = "Increasing"
    DECREASING = "Decreasing"
    NOT_MOVING = "Not Moving"


class SpeedTransformer(Transformer):

    configuration: SpeedTransformerConfiguration
    Source = List[PerceptionObstacle]
    Target = SpeedTransformerResult

    def __init__(self, configuration):
        self.configuration = configuration

    def transform(self, source: Source) -> SpeedTransformerResult:

        linear_velocities = [obstacle.velocity for obstacle in source]
        speed_slopes = self.detect_speed_slope(linear_velocities)

        events = []
        start_time = source[0].timestamp
        for cur, next in zip(speed_slopes[:-1], speed_slopes[1:]):
            duration = source[next[0]].timestamp - source[cur[0]].timestamp

            time_from_start = source[cur[0]].timestamp - start_time
            start_condition = ConditionBuilder.simulation_time_condition(
                rule=Rule.GREATER_THAN, value_in_sec=time_from_start)

            speed = 0
            if cur[1] != SpeedState.NOT_MOVING:
                speed = next[2]

            event_builder = EventBuilder(start_conditions=[start_condition])

            private_action_builder = PrivateActionBuilder()
            private_action_builder.make_absolute_speed_action(
                speed_action_dynamics=SpeedActionDynamics(
                    dynamicsDimension=TransitionDynamics.DynamicsDimension.
                    TIME,
                    dynamicsShape=TransitionDynamics.DynamicsShape.STEP,
                    value=math.floor(duration)),
                value=speed)

            speed_action = private_action_builder.get_result()
            event_builder.add_private_action(name=f"{cur[1].value}",
                                             private_action=speed_action)
            events.append(event_builder.get_result())

        start_condition = ConditionBuilder.simulation_time_condition(
            rule=Rule.GREATER_THAN, value_in_sec=0)

        act = self.wrap_events_to_act(
            events=events,
            start_condition=start_condition,
            entity_names=[self.configuration.entity_name])

        return act

    def detect_speed_slope(self, linear_velocities: List[Point3D]):
        threshold = 0.01
        prev_speed = 0
        cur_speed = 0
        result = []
        for idx, linear_velocity in enumerate(linear_velocities):
            if idx == 0:
                prev_speed = self.calculate_velocity_meter_per_sec(
                    linear_velocity)
                result.append((0, SpeedState.NOT_MOVING, 0))
                continue
            cur_speed = self.calculate_velocity_meter_per_sec(linear_velocity)
            speed_diff = cur_speed - prev_speed

            if abs(speed_diff) > threshold:
                if speed_diff > 0:
                    if result[-1][1] != SpeedState.INCREASING:
                        result.append((idx, SpeedState.INCREASING, cur_speed))
                else:
                    if result[-1][1] != SpeedState.DECREASING:
                        result.append((idx, SpeedState.DECREASING, cur_speed))
            else:
                if speed_diff == 0.0 and result[-1][1] != SpeedState.NOT_MOVING:
                    result.append((idx, SpeedState.NOT_MOVING, cur_speed))

            prev_speed = cur_speed

        result.append(
            (len(linear_velocities) - 1, SpeedState.NOT_MOVING, cur_speed))
        return result

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

    def calculate_velocity_meter_per_sec(self, velocity) -> float:
        x, y, z = velocity.x, velocity.y, velocity.z
        return math.sqrt(x**2 + y**2)
