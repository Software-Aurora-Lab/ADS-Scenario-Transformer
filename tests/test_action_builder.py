import pytest
from openscenario_msgs import GlobalAction, Entities, Position, LanePosition, TransitionDynamics, AbsoluteTargetSpeed, RelativeTargetSpeed, FollowingMode
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
    # Add more assertions as needed


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
