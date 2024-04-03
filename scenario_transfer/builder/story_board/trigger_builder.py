from typing import List
from openscenario_msgs import Trigger, ConditionGroup, Condition
from scenario_transfer.builder import Builder


class TriggerBuilder(Builder):
    product: Trigger

    def make_condition_group(self, conditions: List[Condition]):
        self.product = Trigger(conditionGroups=[ConditionGroup(
            conditions=conditions)]) # It is uncommon to have multiple ConditionGroups. 

    def get_result(self) -> Trigger:
        return self.product
