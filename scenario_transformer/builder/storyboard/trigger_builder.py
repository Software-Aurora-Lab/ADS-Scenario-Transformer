from typing import List
from openscenario_msgs import StartTrigger, StopTrigger, ConditionGroup, Condition
from scenario_transformer.builder import Builder


class StartTriggerBuilder(Builder):
    product: StartTrigger

    def make_condition_group(self, conditions: List[Condition]):
        self.product = StartTrigger(conditionGroups=[
            ConditionGroup(conditions=conditions)
        ])  # It is uncommon to have multiple ConditionGroups.

    def get_result(self) -> StartTrigger:
        return self.product


class StopTriggerBuilder(Builder):
    product: StopTrigger

    def make_condition_group(self, conditions: List[Condition]):
        self.product = StopTrigger(conditionGroups=[
            ConditionGroup(conditions=conditions)
        ])  # It is uncommon to have multiple ConditionGroups.

    def get_result(self) -> StopTrigger:
        return self.product
