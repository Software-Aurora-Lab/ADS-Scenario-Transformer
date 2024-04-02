import pytest
import yaml
from typing import List
from openscenario_msgs import GlobalAction, Entities, Position, LanePosition, WorldPosition, TransitionDynamics, FollowingMode, Properties, Property, Controller, Waypoint, Route, Trajectory, ReferenceContext, TimeReference, Timing, Action, PrivateAction, ByEntityCondition, ByValueCondition, Story, Act, ManeuverGroup, Maneuver, Event, Actors, Trigger
from scenario_transfer.builder.story_board.global_action_builder import GlobalActionBuilder
from scenario_transfer.builder.story_board.private_action_builder import PrivateActionBuilder
from scenario_transfer.builder.story_board.by_entity_condition_builder import ByEntityConditionBuilder
from scenario_transfer.builder.story_board.by_value_condition_builder import ByValueConditionBuilder
from scenario_transfer.builder.entities_builder import EntityType, EntitiesBuilder
from scenario_transfer.openscenario.openscenario_coder import OpenScenarioDecoder


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


@pytest.fixture
def waypoints() -> List[Waypoint]:
    with open("tests/data/openscenario_route.yaml", "r") as file:
        input = file.read()

    dict = yaml.safe_load(input)
    openscenario_route = OpenScenarioDecoder.decode_yaml_to_pyobject(
        yaml_dict=dict, type_=Route, exclude_top_level_key=True)

    return openscenario_route.waypoints


@pytest.fixture
def trajectory() -> Trajectory:
    with open("tests/data/openscenario_trajectory.yaml", "r") as file:
        input = file.read()

    dict = yaml.safe_load(input)
    trajectory = OpenScenarioDecoder.decode_yaml_to_pyobject(
        yaml_dict=dict, type_=Trajectory, exclude_top_level_key=True)
    return trajectory


@pytest.fixture
def time_reference() -> TimeReference:
    return TimeReference(timing=Timing(
        domainAbsoluteRelative=ReferenceContext.REFERENCECONTEXT_RELATIVE,
        offset=0.0,
        scale=1))


@pytest.fixture
def by_entity_collision_condition(ego_name, entities) -> ByEntityCondition:
    colliding_npc_name = entities.scenarioObjects[1].name

    by_entity_condition_builder = ByEntityConditionBuilder(
        triggering_entity=ego_name)
    by_entity_condition_builder.make_collision_condition(
        colliding_entity_name=colliding_npc_name)
    return by_entity_condition_builder.get_result()


@pytest.fixture
def by_value_traffic_condition() -> ByValueCondition:
    by_value_condition_builder = ByValueConditionBuilder()
    by_value_condition_builder.make_traffic_signal_controller_condition(
        phase="test_phase", traffic_signal_controller_name="StraghtSignal")
    return by_value_condition_builder.get_result()


@pytest.fixture
def private_action(lane_position) -> PrivateAction:
    private_action_builder = PrivateActionBuilder()
    private_action_builder.make_teleport_action(lane_position=lane_position)
    return private_action_builder.get_result()


@pytest.fixture
def global_action(lane_position, ego_name) -> GlobalAction:
    global_action_builder = GlobalActionBuilder()
    position = Position(lanePosition=lane_position)
    global_action_builder.make_add_entity_action(position=position,
                                                 entity_name=ego_name)
    return global_action_builder.get_result()


@pytest.fixture
def story() -> Story:
    with open("tests/data/openscenario_story.yaml", "r") as file:
        input = file.read()

    dict = yaml.safe_load(input)

    openscenario_story = OpenScenarioDecoder.decode_yaml_to_pyobject(
        yaml_dict=dict, type_=Story, exclude_top_level_key=True)

    return openscenario_story


@pytest.fixture
def acts(story) -> List[Act]:
    return story.acts


@pytest.fixture
def start_trigger(story) -> Trigger:
    return story.acts[0].startTrigger


@pytest.fixture
def maneuver_groups(acts) -> List[ManeuverGroup]:
    return [
        maneuver_group for act in acts for maneuver_group in act.maneuverGroups
    ]


@pytest.fixture
def maneuvers(maneuver_groups) -> List[Maneuver]:
    return [
        maneuver for maneuver_group in maneuver_groups
        for maneuver in maneuver_group.maneuvers
    ]


@pytest.fixture
def actors(maneuver_groups) -> Actors:
    return maneuver_groups[0].actors


@pytest.fixture
def events(maneuvers) -> List[Event]:
    return [event for maneuver in maneuvers for event in maneuver.events]
