from typing import Optional
from openscenario_msgs import PrivateAction, SpeedAction, LongitudinalAction, TransitionDynamics, SpeedTargetValueType, SpeedActionTarget, AbsoluteTargetSpeed, RelativeTargetSpeed, LateralAction, LaneChangeAction, LaneChangeTarget, AbsoluteTargetLane, RelativeTargetLane
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

    def make_relative_lane_change_action(
            self,
            transition_dynamics: TransitionDynamics,
            entity_name: str,
            value: int,
            lane_offset: Optional[float] = None):
        lane = RelativeTargetLane(entityRef=entity_name, value=value)
        lane_change_target = LaneChangeTarget(relativeTargetLane=lane)

        lane_change_action = LaneChangeAction(
            targetLaneOffset=lane_offset,
            laneChangeActionDynamics=transition_dynamics,
            laneChangeTarget=lane_change_target)
        self.product = PrivateAction(lateralAction=LateralAction(
            laneChangeAction=lane_change_action))

    def make_absolute_lane_change_action(
            self,
            value: str,
            transition_dynamics: TransitionDynamics,
            lane_offset: Optional[float] = None):
        lane = AbsoluteTargetLane(value=value)
        lane_change_target = LaneChangeTarget(absoluteTargetLane=lane)

        lane_change_action = LaneChangeAction(
            targetLaneOffset=lane_offset,
            laneChangeActionDynamics=transition_dynamics,
            laneChangeTarget=lane_change_target)

        self.product = PrivateAction(lateralAction=LateralAction(
            laneChangeAction=lane_change_action))

    def get_result(self) -> PrivateAction:
        return self.product
