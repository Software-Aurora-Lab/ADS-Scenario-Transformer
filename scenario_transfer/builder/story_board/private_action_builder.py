from typing import Optional
from openscenario_msgs import PrivateAction, SpeedAction, LongitudinalAction, TransitionDynamics, SpeedTargetValueType, SpeedActionTarget, AbsoluteTargetSpeed, RelativeTargetSpeed, LateralAction, LaneChangeAction, LaneChangeTarget, AbsoluteTargetLane, RelativeTargetLane, AssignControllerAction, ControllerAction, CatalogReference, Controller, TeleportAction, Position, LanePosition, WorldPosition
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

    def make_assign_controller_action(
            self,
            controller: Controller,
            activate_lateral: Optional[bool] = None,
            activate_lighting: Optional[bool] = None,
            activate_longitudinal: Optional[bool] = None,
            catalog_reference: Optional[CatalogReference] = None):
        assign_controller_action = AssignControllerAction(
            activateLateral=activate_lateral,
            activateLighting=activate_lighting,
            activateLongitudinal=activate_longitudinal,
            controller=controller,
            catalogReference=catalog_reference)
        self.product = PrivateAction(controllerAction=ControllerAction(assignControllerAction=assign_controller_action))

    def make_teleport_action(self,
                             lane_position: Optional[LanePosition] = None,
                             world_position: Optional[WorldPosition] = None):
        assert lane_position is not None or world_position is not None, "TeleportAction needs one type of position"

        position = None
        if lane_position is not None:
            position = Position(lanePosition=lane_position)
        else:
            position = Position(worldPosition=world_position)

        self.product = PrivateAction(teleportAction=TeleportAction(position=position))

    def get_result(self) -> PrivateAction:
        return self.product
