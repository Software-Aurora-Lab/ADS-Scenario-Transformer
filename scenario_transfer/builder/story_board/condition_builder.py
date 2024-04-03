from openscenario_msgs import Condition, ByEntityCondition, ByValueCondition
from scenario_transfer.builder import Builder


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
