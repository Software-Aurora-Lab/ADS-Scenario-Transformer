import pytest
from openscenario_msgs import GlobalAction, Entities, Position, LanePosition, WorldPosition, TransitionDynamics, AbsoluteTargetSpeed, RelativeTargetSpeed, FollowingMode, Properties, Property, Controller, ControllerAction, AssignControllerAction, TeleportAction
from openscenario_msgs.common_pb2 import InfrastructureAction, EntityAction, LaneChangeAction, UserDefinedAction, PrivateAction, SpeedTargetValueType, SpeedAction
from scenario_transfer.builder.story_board.global_action_builder import GlobalActionBuilder
from scenario_transfer.builder.story_board.user_defined_action_builder import UserDefinedActionBuilder
from scenario_transfer.builder.story_board.private_action_builder import PrivateActionBuilder
from scenario_transfer.builder.entities_builder import EntityType, EntitiesBuilder

@pytest.fixture
def entities() -> Entities:
    builder = EntitiesBuilder(entities=[
        EntityType.NPC, EntityType.NPC, EntityType.EGO, EntityType.PEDESTRIAN,
        EntityType.NPC
    ])
    return builder.get_result()


@pytest.fixture
def ego_name(entities) -> str:
    return entities.scenarioObjects[0].name


@pytest.fixture
def transition_dynamics() -> TransitionDynamics:
    return TransitionDynamics(
        dynamicsDimension=TransitionDynamics.DynamicsDimension.RATE,
        dynamicsShape=TransitionDynamics.DynamicsShape.LINEAR,
        followingMode=FollowingMode.FOLLOWINGMODE_FOLLOW,
        value=1.0)

@pytest.fixture
def properties() -> Properties:
    return Properties(properties=[
        Property(name="isEgo", value="true"),
        Property(name="maxSpeed", value="50")
    ])

@pytest.fixture
def controller(properties) -> Controller:
    return Controller(name="controller",
                      properties=properties,
                      parameterDeclarations=[])

@pytest.fixture
def lane_position() -> LanePosition:
    return LanePosition(laneId="154", s=10.9835, offset=-0.5042)

@pytest.fixture
def world_position() -> WorldPosition:
    return WorldPosition(x=37.416880423172465, y=-122.01593194093681, z=0.0)

def assert_proto_type_equal(reflection_type, pb2_type):
    assert str(reflection_type.__class__) == str(pb2_type)


def test_global_action_builder_add_entity_action(ego_name):
    assert ego_name == "ego"
    builder = GlobalActionBuilder()

    position = Position(
        lanePosition=LanePosition(laneId="154", s=10.9835, offset=-0.5042))

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


def test_relative_speed_action_builder(ego_name, transition_dynamics):
    assert ego_name == "ego"
    builder = PrivateActionBuilder()
    builder.make_relative_speed_action(
        transition_dynamics=transition_dynamics,
        continuous=True,
        entity_name=ego_name,
        target_value_type=SpeedTargetValueType.SPEEDTARGETVALUETYPE_DELTA,
        value=2.0)

    action = builder.get_result()
    assert_proto_type_equal(action, PrivateAction)
    speed_action = action.longitudinalAction.speedAction
    assert_proto_type_equal(speed_action, SpeedAction)
    assert_proto_type_equal(speed_action.speedActionDynamics,
                            TransitionDynamics)
    assert_proto_type_equal(speed_action.speedActionTarget.relativeTargetSpeed,
                            RelativeTargetSpeed)


def test_absolute_speed_action_builder(transition_dynamics):
    builder = PrivateActionBuilder()
    builder.make_absolute_speed_action(transition_dynamics=transition_dynamics,
                                       value=0.0)
    action = builder.get_result()
    assert_proto_type_equal(action, PrivateAction)
    speed_action = action.longitudinalAction.speedAction
    assert_proto_type_equal(speed_action, SpeedAction)
    assert_proto_type_equal(speed_action.speedActionDynamics,
                            TransitionDynamics)
    assert_proto_type_equal(speed_action.speedActionTarget.absoluteTargetSpeed,
                            AbsoluteTargetSpeed)


def test_relative_lane_change_action(transition_dynamics):
    builder = PrivateActionBuilder()
    builder.make_relative_lane_change_action(
        transition_dynamics=transition_dynamics,
        entity_name="example_entity",
        value=2,
        lane_offset=0.5)
    action = builder.get_result()
    assert action is not None
    assert_proto_type_equal(action.lateralAction.laneChangeAction,
                            LaneChangeAction)
    assert_proto_type_equal(
        action.lateralAction.laneChangeAction.laneChangeActionDynamics,
        TransitionDynamics)


def test_absolute_lane_change_action(transition_dynamics):
    builder = PrivateActionBuilder()
    builder.make_absolute_lane_change_action(
        transition_dynamics=transition_dynamics,
        value="example_value",
        lane_offset=0.5)
    action = builder.get_result()
    assert action is not None
    assert_proto_type_equal(action.lateralAction.laneChangeAction,
                            LaneChangeAction)
    assert_proto_type_equal(
        action.lateralAction.laneChangeAction.laneChangeActionDynamics,
        TransitionDynamics)

def test_assigned_control_action(controller):
    builder = PrivateActionBuilder()
    builder.make_assign_controller_action(
            controller= controller,
            activate_lateral=True)
    action = builder.get_result()

    assert action is not None
    assert_proto_type_equal(action.controllerAction, ControllerAction)
    assert_proto_type_equal(action.controllerAction.assignControllerAction, AssignControllerAction)
    target_controller = action.controllerAction.assignControllerAction.controller
    assert target_controller.properties.properties[0].name == "isEgo"
    assert target_controller.properties.properties[1].name == "maxSpeed"

def test_teleport_action(world_position, lane_position):
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