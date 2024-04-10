from openscenario_msgs import GlobalAction, Position, LanePosition, WorldPosition, SpeedActionDynamics, LaneChangeActionDynamics, AbsoluteTargetSpeed, RelativeTargetSpeed, FollowingMode, ControllerAction, AssignControllerAction, TeleportAction, Action
from openscenario_msgs.common_pb2 import InfrastructureAction, EntityAction, LaneChangeAction, UserDefinedAction, PrivateAction, SpeedTargetValueType, SpeedAction
from scenario_transfer.builder.story_board.global_action_builder import GlobalActionBuilder
from scenario_transfer.builder.story_board.user_defined_action_builder import UserDefinedActionBuilder
from scenario_transfer.builder.story_board.private_action_builder import PrivateActionBuilder
from scenario_transfer.builder.story_board.routing_action_builder import RoutingActionBuilder
from scenario_transfer.builder.story_board.action_builder import ActionBuilder


def assert_proto_type_equal(reflection_type, pb2_type):
    assert str(reflection_type.__class__) == str(pb2_type)


def test_global_action_builder_add_entity_action(ego_name, lane_position):
    assert ego_name == "ego"
    builder = GlobalActionBuilder()

    position = Position(lanePosition=lane_position)
    builder.make_add_entity_action(position=position, entity_name=ego_name)
    action = builder.get_result()

    assert isinstance(action, GlobalAction)
    assert action.entityAction.entityRef == ego_name
    assert action.entityAction.addEntityAction.position.lanePosition.laneId == "154"


def test_global_action_builder_delete_entity_action(ego_name):
    assert ego_name == "ego"
    builder = GlobalActionBuilder()
    builder.make_delete_entity_action(entity_name=ego_name)
    action = builder.get_result()

    assert isinstance(action, GlobalAction)
    assert_proto_type_equal(action.entityAction, EntityAction)
    assert action.entityAction.entityRef == ego_name
    assert action.entityAction.deleteEntityAction is not None


def test_global_action_builder_traffic_signal_controller_action():

    builder = GlobalActionBuilder()
    builder.make_traffic_signal_controller_action(
        phase="test_phase", traffic_signal_controller_name="StraghtSignal")

    action = builder.get_result()

    assert isinstance(action, GlobalAction)
    assert_proto_type_equal(action.infrastructureAction, InfrastructureAction)

    assert action.infrastructureAction.trafficSignalAction.trafficSignalControllerAction.trafficSignalControllerRef == "StraghtSignal"


def test_global_action_builder_traffic_signal_state_action():
    builder = GlobalActionBuilder()
    builder.make_traffic_signal_state_action(name="StraghtSignal",
                                             state="green")

    action = builder.get_result()

    assert isinstance(action, GlobalAction)
    assert_proto_type_equal(action.infrastructureAction, InfrastructureAction)
    assert action.infrastructureAction.trafficSignalAction.trafficSignalStateAction.name == "StraghtSignal"


def test_user_definec_action_builder():
    builder = UserDefinedActionBuilder()

    builder.make_custom_command_action(type=":", content="")
    null_action = builder.get_result()

    assert_proto_type_equal(null_action, UserDefinedAction)


def test_relative_speed_action_builder(ego_name, speed_action_dynamics):
    assert ego_name == "ego"
    builder = PrivateActionBuilder()
    builder.make_relative_speed_action(
        speed_action_dynamics=speed_action_dynamics,
        continuous=True,
        entity_name=ego_name,
        target_value_type=SpeedTargetValueType.SPEEDTARGETVALUETYPE_DELTA,
        value=2.0)

    action = builder.get_result()
    assert_proto_type_equal(action, PrivateAction)
    speed_action = action.longitudinalAction.speedAction
    assert_proto_type_equal(speed_action, SpeedAction)
    assert_proto_type_equal(speed_action.speedActionDynamics,
                            SpeedActionDynamics)
    assert_proto_type_equal(speed_action.speedActionTarget.relativeTargetSpeed,
                            RelativeTargetSpeed)


def test_absolute_speed_action_builder(speed_action_dynamics):
    builder = PrivateActionBuilder()
    builder.make_absolute_speed_action(
        speed_action_dynamics=speed_action_dynamics, value=0.0)
    action = builder.get_result()
    assert_proto_type_equal(action, PrivateAction)
    speed_action = action.longitudinalAction.speedAction
    assert_proto_type_equal(speed_action, SpeedAction)
    assert_proto_type_equal(speed_action.speedActionDynamics,
                            SpeedActionDynamics)
    assert_proto_type_equal(speed_action.speedActionTarget.absoluteTargetSpeed,
                            AbsoluteTargetSpeed)


def test_relative_lane_change_action_builder(lane_change_action_dynamics):
    builder = PrivateActionBuilder()
    builder.make_relative_lane_change_action(
        lane_change_action_dynamics=lane_change_action_dynamics,
        entity_name="example_entity",
        value=2,
        lane_offset=0.5)
    action = builder.get_result()
    assert action is not None
    assert_proto_type_equal(action.lateralAction.laneChangeAction,
                            LaneChangeAction)
    assert_proto_type_equal(
        action.lateralAction.laneChangeAction.laneChangeActionDynamics,
        LaneChangeActionDynamics)


def test_absolute_lane_change_action_builder(lane_change_action_dynamics):
    builder = PrivateActionBuilder()
    builder.make_absolute_lane_change_action(
        lane_change_action_dynamics=lane_change_action_dynamics,
        value="example_value",
        lane_offset=0.5)
    action = builder.get_result()
    assert action is not None
    assert_proto_type_equal(action.lateralAction.laneChangeAction,
                            LaneChangeAction)
    assert_proto_type_equal(
        action.lateralAction.laneChangeAction.laneChangeActionDynamics,
        LaneChangeActionDynamics)


def test_assigned_control_action_builder(controller):
    builder = PrivateActionBuilder()
    builder.make_assign_controller_action(controller=controller,
                                          activate_lateral=True)
    action = builder.get_result()

    assert action is not None
    assert_proto_type_equal(action.controllerAction, ControllerAction)
    assert_proto_type_equal(action.controllerAction.assignControllerAction,
                            AssignControllerAction)
    target_controller = action.controllerAction.assignControllerAction.controller
    assert target_controller.properties.properties[0].name == "isEgo"
    assert target_controller.properties.properties[1].name == "maxSpeed"


def test_teleport_action_builder(world_position, lane_position):
    builder = PrivateActionBuilder()
    builder.make_teleport_action(lane_position=lane_position)
    action = builder.get_result()

    assert action is not None
    assert_proto_type_equal(action.teleportAction, TeleportAction)
    lane_position_in_teleport_action = action.teleportAction.position.lanePosition
    assert_proto_type_equal(lane_position_in_teleport_action, LanePosition)
    assert lane_position_in_teleport_action.laneId == "154"
    assert lane_position_in_teleport_action.s == 10.9835
    assert lane_position_in_teleport_action.offset == -0.5042

    builder.make_teleport_action(world_position=world_position)
    action = builder.get_result()
    assert action is not None
    assert_proto_type_equal(action.teleportAction, TeleportAction)
    world_position_in_teleport_action = action.teleportAction.position.worldPosition
    assert_proto_type_equal(world_position_in_teleport_action, WorldPosition)
    assert world_position_in_teleport_action.x == 37.416880423172465
    assert world_position_in_teleport_action.y == -122.01593194093681
    assert world_position_in_teleport_action.z == 0.0


def test_acquire_position_action_builder(world_position, lane_position):
    builder = RoutingActionBuilder()
    builder.make_acquire_position_action(lane_position=lane_position)

    routing_action = builder.get_result()
    assert routing_action is not None

    lane_position = routing_action.acquirePositionAction.position.lanePosition
    assert lane_position.laneId == "154"
    assert lane_position.s == 10.9835
    assert lane_position.offset == -0.5042

    builder.make_acquire_position_action(world_position=world_position)
    routing_action = builder.get_result()

    assert routing_action is not None
    world_position = routing_action.acquirePositionAction.position.worldPosition
    assert world_position.x == 37.416880423172465
    assert world_position.y == -122.01593194093681
    assert world_position.z == 0.0


def test_assign_route_action_builder(waypoints):
    assert waypoints is not None

    builder = RoutingActionBuilder()
    builder.make_assign_route_action(closed=True,
                                     name="AssignRouteAction",
                                     parameter_declarations=[],
                                     waypoints=waypoints)
    routing_action = builder.get_result()
    assert routing_action is not None
    route = routing_action.assignRouteAction.route
    assert route.closed == True
    assert route.name == "AssignRouteAction"
    waypoint = route.waypoints[0]
    assert waypoint.position.lanePosition.laneId == "22"
    assert waypoint.position.lanePosition.s == 35.71471492399046
    assert waypoint.position.lanePosition.orientation.h == 2.883901414579166


def test_following_trajectory_action_builder(trajectory, time_reference):
    assert trajectory is not None
    builder = RoutingActionBuilder()

    builder.make_following_trajectory_action(timing=time_reference.timing,
                                             trajectory=trajectory,
                                             initial_offset=0.0)
    routing_action = builder.get_result()
    assert routing_action is not None
    follow_trajectory_action = routing_action.followTrajectoryAction
    assert follow_trajectory_action.timeReference.timing.offset == 0
    assert follow_trajectory_action.trajectoryFollowingMode.followingMode == FollowingMode.FOLLOWINGMODE_POSITION
    trajectory = follow_trajectory_action.trajectoryRef.trajectory
    assert trajectory.name == "ego_approach"
    assert trajectory.closed == False
    assert len(trajectory.shape.polyline.vertices) == 5


def test_action_builder(lane_position, ego_name):
    builder = ActionBuilder()

    private_action_builder = PrivateActionBuilder()
    private_action_builder.make_teleport_action(lane_position=lane_position)
    private_action = private_action_builder.get_result()

    builder.make_action(name="test_action", private_action=private_action)

    action = builder.get_result()
    assert_proto_type_equal(action, Action)
    assert_proto_type_equal(action.privateAction.teleportAction,
                            TeleportAction)
    lane_position_in_teleport_action = action.privateAction.teleportAction.position.lanePosition
    assert_proto_type_equal(lane_position_in_teleport_action, LanePosition)
    assert lane_position_in_teleport_action.laneId == "154"
    assert lane_position_in_teleport_action.s == 10.9835
    assert lane_position_in_teleport_action.offset == -0.5042

    global_action_builder = GlobalActionBuilder()
    position = Position(lanePosition=lane_position)
    global_action_builder.make_add_entity_action(position=position,
                                                 entity_name=ego_name)
    global_action = global_action_builder.get_result()

    builder.make_action(name="test_action", global_action=global_action)
    action = builder.get_result()
    assert_proto_type_equal(action, Action)
    assert action.globalAction.entityAction.entityRef == ego_name
    assert action.globalAction.entityAction.addEntityAction.position.lanePosition.laneId == "154"
