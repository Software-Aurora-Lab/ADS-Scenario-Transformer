from openscenario_msgs import Rule
from openscenario_msgs.common_pb2 import ByValueCondition, SimulationTimeCondition, StoryboardElementStateCondition, TimeOfDayCondition, VariableCondition, UserDefinedValueCondition
from openscenario_msgs.parameter_pb2 import ParameterCondition, ParameterDeclaration
from openscenario_msgs.traffic_signal_pb2 import TrafficSignalCondition, TrafficSignalControllerCondition
from ads_scenario_transformer.builder import Builder


class ByValueConditionBuilder(Builder):

    product: ByValueCondition

    def __init__(self):
        pass

    def make_parameter_condition(self,
                                 parameter_declaration: ParameterDeclaration,
                                 rule: Rule, value: str):
        self.condition = ParameterCondition(parameterRef=parameter_declaration,
                                            rule=rule,
                                            value=value)
        self.product = ByValueCondition(parameterCondition=self.condition)

    def make_simulation_time_condition(self, rule: Rule, value_in_sec: float):
        self.condition = SimulationTimeCondition(rule=rule, value=value_in_sec)
        self.product = ByValueCondition(simulationTimeCondition=self.condition)

    def make_storyboard_element_state_condition(
            self, state: StoryboardElementStateCondition.State,
            element_name: str, type: StoryboardElementStateCondition.Type):

        self.condition = StoryboardElementStateCondition(
            state=state,
            storyboardElementRef=element_name,
            storyboardElementType=type)
        self.product = ByValueCondition(
            storyboardElementStateCondition=self.condition)

    def make_user_defined_value_condition(self, name: str, rule: Rule,
                                          value: str):
        self.condition = UserDefinedValueCondition(name=name,
                                                   rule=rule,
                                                   value=value)
        self.product = ByValueCondition(
            userDefinedValueCondition=self.condition)

    def make_traffic_signal_condition(self, name: str, state: str):
        self.condition = TrafficSignalCondition(name=name, state=state)
        self.product = ByValueCondition(trafficSignalCondition=self.condition)

    def make_traffic_signal_controller_condition(
            self, phase: str, traffic_signal_controller_name: str):

        self.condition = TrafficSignalControllerCondition(
            phase=phase,
            trafficSignalControllerRef=traffic_signal_controller_name)
        self.product = ByValueCondition(
            trafficSignalControllerCondition=self.condition)

    def get_result(self) -> ByValueCondition:
        assert self.product is not None
        return self.product

    # Unsupported condition types

    def make_time_of_day_condition(self):
        raise TypeError(
            f"Unsupported type: {type(TimeOfDayCondition()).__name__}")

    def make_variable_condition(self):
        raise TypeError(
            f"Unsupported type: {type(VariableCondition()).__name__}")
