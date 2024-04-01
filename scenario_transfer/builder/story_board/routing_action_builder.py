from typing import List, Optional
from openscenario_msgs import RoutingAction, Waypoint, Route, ParameterDeclaration, AssignRouteAction, Position, LanePosition, WorldPosition, AcquirePositionAction, FollowTrajectoryAction, TrajectoryRef, Trajectory, TrajectoryFollowingMode, FollowingMode, Timing, TimeReference
from scenario_transfer import Builder


class RoutingActionBuilder(Builder):
    product: RoutingAction

    def make_assign_route_action(
            self, closed: bool, name: str,
            parameter_declarations: List[ParameterDeclaration],
            waypoints: List[Waypoint]):
        assert len(
            waypoints) > 1, "The number of waypoints should be larger than 2"
        route = Route(closed=closed,
                      name=name,
                      parameterDeclarations=parameter_declarations,
                      waypoints=waypoints)
        self.product = RoutingAction(assignRouteAction=AssignRouteAction(
            route=route))

    def make_acquire_position_action(
            self,
            lane_position: Optional[LanePosition] = None,
            world_position: Optional[WorldPosition] = None):
        assert lane_position is not None or world_position is not None, "AcquirePositionAction needs one type of position"

        position = None
        if lane_position is not None:
            position = Position(lanePosition=lane_position)
        else:
            position = Position(worldPosition=world_position)
        self.product = RoutingAction(
            acquirePositionAction=AcquirePositionAction(position=position))

    def make_following_trajectory_action(
            self,
            timing: Optional[Timing],
            trajectory: Trajectory,
            initial_offset: Optional[float] = None):

        time_reference = TimeReference(none=TimeReference.NONE())

        if timing:
            time_reference = TimeReference(timing=timing)

        followingMode = TrajectoryFollowingMode(
            followingMode=FollowingMode.FOLLOWINGMODE_POSITION)
        self.product = RoutingAction(
            followTrajectoryAction=FollowTrajectoryAction(
                initialDistanceOffset=initial_offset,
                timeReference=time_reference,
                trajectoryFollowingMode=followingMode,
                trajectoryRef=TrajectoryRef(trajectory=trajectory)))

    def get_result(self) -> RoutingAction:
        return self.product
