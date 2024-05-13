from typing import List
from openscenario_msgs import StartTrigger, StopTrigger, ConditionGroup, Condition
from ads_scenario_transformer.builder import Builder


class StartTriggerBuilder(Builder):
    product: StartTrigger

    def make_condition_group(self, conditions: List[Condition]):

        self.product = StartTrigger(conditionGroups=[
            ConditionGroup(conditions=[condition]) for condition in conditions
        ])

    def get_result(self) -> StartTrigger:
        return self.product


class StopTriggerBuilder(Builder):
    product: StopTrigger

    def make_condition_group(self, conditions: List[Condition]):

        self.product = StopTrigger(conditionGroups=[
            ConditionGroup(conditions=[condition]) for condition in conditions
        ])

    def get_result(self) -> StopTrigger:
        return self.product
