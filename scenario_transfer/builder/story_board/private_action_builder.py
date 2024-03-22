from openscenario_msgs import PrivateAction, SpeedAction, LongitudinalAction, TransitionDynamics, SpeedTargetValueType, SpeedActionTarget
from openscenario_msgs.common_pb2 import AbsoluteTargetSpeed, RelativeTargetSpeed
from scenario_transfer.builder.builder import Builder


class PrivateActionBuilder(Builder):
    product: PrivateAction

    def make_relative_speed_action(self,
                                   transition_dynamics: TransitionDynamics,
                                   continuous: bool, entity_name: str,
                                   target_value_type: SpeedTargetValueType,
                                   value: float):
        target_speed = RelativeTargetSpeed(
            continuous=continuous,
            entityRef=entity_name,
            speedTargetValueType=target_value_type,
            value=value)
        action = SpeedAction(speedActionDynamics=transition_dynamics,
                             speedActionTarget=SpeedActionTarget(
                                 relativeTargetSpeed=target_speed))
        self.product = PrivateAction(longitudinalAction=LongitudinalAction(
            speedAction=action))

    def make_absolute_speed_action(self,
                                   transition_dynamics: TransitionDynamics,
                                   value: float):
        target_speed = AbsoluteTargetSpeed(value=value)
        action = SpeedAction(speedActionDynamics=transition_dynamics,
                             speedActionTarget=SpeedActionTarget(
                                 absoluteTargetSpeed=target_speed))

        self.product = PrivateAction(longitudinalAction=LongitudinalAction(
            speedAction=action))

    def get_result(self) -> PrivateAction:
        return self.product
