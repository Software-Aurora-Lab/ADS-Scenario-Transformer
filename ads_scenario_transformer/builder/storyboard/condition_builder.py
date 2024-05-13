from typing import List
from openscenario_msgs import Condition, ByEntityCondition, ByValueCondition, Rule, ScenarioObject
from ads_scenario_transformer.builder import Builder
from ads_scenario_transformer.builder.storyboard.by_value_condition_builder import ByValueConditionBuilder
from ads_scenario_transformer.builder.storyboard.by_entity_condition_builder import ByEntityConditionBuilder


class ConditionBuilder(Builder):
    product: Condition

    def __init__(
        self,
        name="",
        delay: float = 0,
        condition_edge: Condition.ConditionEdge = Condition.ConditionEdge.NONE
    ):
        self.name = name
        self.delay = delay
        self.condition_edge = condition_edge

    def make_by_entity_condition(self, by_entity_condition: ByEntityCondition):
        self.product = Condition(name=self.name,
                                 delay=self.delay,
                                 conditionEdge=self.condition_edge,
                                 byEntityCondition=by_entity_condition,
                                 byValueCondition=None)

    def make_by_value_condition(self, by_value_condition: ByValueCondition):
        self.product = Condition(name=self.name,
                                 delay=self.delay,
                                 conditionEdge=self.condition_edge,
                                 byEntityCondition=None,
                                 byValueCondition=by_value_condition)

    def get_result(self) -> Condition:
        return self.product

    @staticmethod
    def simulation_time_condition(rule: Rule,
                                  value_in_sec: float) -> Condition:
        builder = ByValueConditionBuilder()
        builder.make_simulation_time_condition(rule=rule,
                                               value_in_sec=value_in_sec)
        by_value_condition = builder.get_result()

        condition_builder = ConditionBuilder()
        condition_builder.make_by_value_condition(by_value_condition)
        return condition_builder.get_result()

    @staticmethod
    def ego_start_moving_condition(delay: float) -> Condition:
        builder = ByEntityConditionBuilder(triggering_entity="ego")
        builder.make_speed_condition(value_in_ms=0.0, rule=Rule.GREATER_THAN)
        by_entity_condition = builder.get_result()

        condition_builder = ConditionBuilder(delay=delay)
        condition_builder.make_by_entity_condition(by_entity_condition)
        return condition_builder.get_result()

    @staticmethod
    def ego_collision_conditions(
            colliding_entities: List[ScenarioObject]) -> List[Condition]:
        builder = ByEntityConditionBuilder(triggering_entity="ego")
        conditions = []
        for colliding_entity in colliding_entities:
            builder.make_collision_condition(
                colliding_entity_name=colliding_entity.name)

            by_entity_condition = builder.get_result()
            condition_builder = ConditionBuilder(delay=0)
            condition_builder.make_by_entity_condition(by_entity_condition)
            conditions.append(condition_builder.get_result())

        return conditions

    @staticmethod
    def ego_acceleration_conditions(threshold=2.5) -> List[Condition]:
        builder = ByEntityConditionBuilder(triggering_entity="ego")

        conditions = []
        for value, rule in [(threshold, Rule.GREATER_THAN),
                            (-threshold, Rule.LESS_THAN)]:
            builder.make_acceleration_condition(value_in_ms=value, rule=rule)
            by_entity_condition = builder.get_result()
            condition_builder = ConditionBuilder(delay=0)
            condition_builder.make_by_entity_condition(by_entity_condition)
            conditions.append(condition_builder.get_result())

        return conditions
