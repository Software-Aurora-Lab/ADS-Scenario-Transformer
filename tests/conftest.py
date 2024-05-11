import pytest
import yaml
from typing import List
from openscenario_msgs import GlobalAction, Entities, Position, LanePosition, WorldPosition, SpeedActionDynamics, LaneChangeActionDynamics, TransitionDynamics, FollowingMode, Properties, Property, Controller, Waypoint, Route, Trajectory, ReferenceContext, TimeReference, Timing, PrivateAction, ByEntityCondition, ByValueCondition, Story, Act, ManeuverGroup, Maneuver, Event, Actors, StartTrigger, StopTrigger, Storyboard, Actions, Scenario, ParameterDeclarations, ParameterDeclaration, ParameterType
from ads_scenario_transformer.builder.storyboard.global_action_builder import GlobalActionBuilder
from ads_scenario_transformer.builder.storyboard.private_action_builder import PrivateActionBuilder
from ads_scenario_transformer.builder.storyboard.by_entity_condition_builder import ByEntityConditionBuilder
from ads_scenario_transformer.builder.storyboard.by_value_condition_builder import ByValueConditionBuilder
from ads_scenario_transformer.builder.parameter_declarations_builder import ParameterDeclarationsBuilder
from ads_scenario_transformer.builder.entities_builder import ASTEntityType, EntitiesBuilder, ASTEntity
from ads_scenario_transformer.openscenario.openscenario_coder import OpenScenarioDecoder
from ads_scenario_transformer.builder.scenario_builder import ScenarioBuilder, ScenarioConfiguration
from modules.localization.proto.localization_pb2 import LocalizationEstimate
from ads_scenario_transformer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel

import lanelet2
from lanelet2.projection import MGRSProjector
from lanelet2.io import Origin
from lanelet2.core import LaneletMap
from ads_scenario_transformer.tools.apollo_map_parser import ApolloMapParser
from ads_scenario_transformer.tools.vector_map_parser import VectorMapParser
from definitions import SAMPLE_ROOT


@pytest.fixture
def mgrs_projector() -> MGRSProjector:
    origin = Origin(37.04622247590861, -123.00000000000001, 0)
    return MGRSProjector(origin)


@pytest.fixture
def borregas_scenorita_scenario1_path() -> str:
    return SAMPLE_ROOT + "/apollo_borregas/scenoRITA/00000001.00000"


@pytest.fixture
def borregas_scenorita_scenario9_path() -> str:
    return SAMPLE_ROOT + "/apollo_borregas/scenoRITA/00000009.00000"


@pytest.fixture
def borregas_scenorita_scenario23_path() -> str:
    return SAMPLE_ROOT + "/apollo_borregas/scenoRITA/00000023.00000"


@pytest.fixture
def borregas_scenorita_scenario34_path() -> str:
    return SAMPLE_ROOT + "/apollo_borregas/scenoRITA/00000034.00000"


@pytest.fixture
def borregas_scenorita_scenario75_path() -> str:
    return SAMPLE_ROOT + "/apollo_borregas/scenoRITA/00000075.00000"

@pytest.fixture
def borregas_scenorita_scenario94_path() -> str:
    return SAMPLE_ROOT + "/apollo_borregas/scenoRITA/00000094.00000"

@pytest.fixture
def borregas_scenorita_scenario140_path() -> str:
    return SAMPLE_ROOT + "/apollo_borregas/scenoRITA/00000140.00000"


@pytest.fixture
def borregas_doppel_scenario160_path() -> str:
    return SAMPLE_ROOT + "/apollo_borregas/DoppelTest/00000160.00000"


@pytest.fixture
def borregas_doppel_scenario48_path() -> str:
    return SAMPLE_ROOT + "/apollo_borregas/DoppelTest/00000048.00000"


@pytest.fixture
def borregas_doppel_scenario9_path() -> str:
    return SAMPLE_ROOT + "/apollo_borregas/DoppelTest/00000009.00000"


@pytest.fixture
def sf_doppel_scenario_path() -> str:
    return SAMPLE_ROOT + "/apollo_sanfrancisco/DoppelTest/apollo_dev_ROUTE_0.Scenario_00007.00000"


@pytest.fixture
def borregas_vector_map_path() -> str:
    return SAMPLE_ROOT + "/map/BorregasAve/lanelet2_map.osm"


@pytest.fixture
def borregas_apollo_map_path() -> str:
    return SAMPLE_ROOT + "/map/BorregasAve/base_map.bin"


@pytest.fixture
def lanelet_map(borregas_vector_map_path, mgrs_projector) -> LaneletMap:
    return lanelet2.io.load(borregas_vector_map_path, mgrs_projector)


@pytest.fixture
def apollo_map_parser(borregas_apollo_map_path) -> ApolloMapParser:
    return ApolloMapParser(filepath=borregas_apollo_map_path)


@pytest.fixture
def vector_map_parser(borregas_vector_map_path) -> ApolloMapParser:
    return VectorMapParser(borregas_vector_map_path)


@pytest.fixture
def localization_poses(
        borregas_doppel_scenario48_path) -> List[LocalizationEstimate]:
    return CyberRecordReader.read_channel(
        source_path=borregas_doppel_scenario48_path,
        channel=CyberRecordChannel.LOCALIZATION_POSE)


@pytest.fixture
def scenario(storyboard) -> Scenario:
    ast_entities = [
        ASTEntity(entity_type=ASTEntityType.EGO,
                  use_default_scenario_object=True),
        ASTEntity(entity_type=ASTEntityType.CAR,
                  use_default_scenario_object=True),
        ASTEntity(entity_type=ASTEntityType.CAR,
                  use_default_scenario_object=True)
    ]
    entities_builder = EntitiesBuilder()
    for ast_entity in ast_entities:
        entities_builder.add_entity(ast_entity)

    entities = entities_builder.get_result()

    scenario_config = ScenarioConfiguration(
        entities=entities,
        lanelet_map_path="/home/map/lanelet2.osm",
        traffic_signals=[])
    scenario_builder = ScenarioBuilder(scenario_configuration=scenario_config)
    scenario_builder.make_scenario_definition(storyboard=storyboard)
    return scenario_builder.get_result()


@pytest.fixture
def ast_entities() -> List[ASTEntity]:
    return [
        ASTEntity(entity_type=ASTEntityType.CAR,
                  use_default_scenario_object=True),
        ASTEntity(embedding_id=100,
                  entity_type=ASTEntityType.CAR,
                  use_default_scenario_object=True),
        ASTEntity(entity_type=ASTEntityType.EGO,
                  use_default_scenario_object=True),
        ASTEntity(embedding_id=200,
                  entity_type=ASTEntityType.PEDESTRIAN,
                  use_default_scenario_object=True),
        ASTEntity(embedding_id=300,
                  entity_type=ASTEntityType.CAR,
                  use_default_scenario_object=True)
    ]


@pytest.fixture
def entities(ast_entities) -> Entities:
    builder = EntitiesBuilder()
    for ast_entity in ast_entities:
        builder.add_entity(ast_entity)
    return builder.get_result()


@pytest.fixture
def ego_name(entities) -> str:
    return entities.scenarioObjects[0].name


@pytest.fixture
def speed_action_dynamics() -> SpeedActionDynamics:
    return SpeedActionDynamics(
        dynamicsDimension=TransitionDynamics.DynamicsDimension.RATE,
        dynamicsShape=TransitionDynamics.DynamicsShape.LINEAR,
        followingMode=FollowingMode.FOLLOWINGMODE_FOLLOW,
        value=1.0)


@pytest.fixture
def lane_change_action_dynamics() -> LaneChangeActionDynamics:
    return LaneChangeActionDynamics(
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
def storyboard() -> Storyboard:
    with open("tests/data/openscenario_storyboard.yaml", "r") as file:
        input = file.read()

    dict = yaml.safe_load(input)

    openscenario_storyboard = OpenScenarioDecoder.decode_yaml_to_pyobject(
        yaml_dict=dict, type_=Storyboard, exclude_top_level_key=True)

    return openscenario_storyboard


@pytest.fixture
def init_actions(storyboard) -> Actions:
    return storyboard.init.actions


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
def start_trigger(story) -> StartTrigger:
    return story.acts[0].startTrigger


@pytest.fixture
def stop_trigger(storyboard) -> StopTrigger:
    return storyboard.stopTrigger


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


@pytest.fixture
def parameter_declarations() -> ParameterDeclarations:

    declarations = [
        ParameterDeclaration(name='ego_speed',
                             parameterType=ParameterType.PARAMETERTYPE_DOUBLE,
                             value='__tier4_modifier_ego_speed'),
        ParameterDeclaration(name='npc_position',
                             parameterType=ParameterType.PARAMETERTYPE_DOUBLE,
                             value='__tier4_modifier_npc_position'),
        ParameterDeclaration(name='__ego_dimensions_length__',
                             parameterType=ParameterType.PARAMETERTYPE_DOUBLE,
                             value='0'),
        ParameterDeclaration(name='__ego_dimensions_width__',
                             parameterType=ParameterType.PARAMETERTYPE_DOUBLE,
                             value='0'),
        ParameterDeclaration(name='__ego_dimensions_height__',
                             parameterType=ParameterType.PARAMETERTYPE_DOUBLE,
                             value='0'),
        ParameterDeclaration(name='__ego_center_x__',
                             parameterType=ParameterType.PARAMETERTYPE_DOUBLE,
                             value='0'),
        ParameterDeclaration(name='__ego_center_y__',
                             parameterType=ParameterType.PARAMETERTYPE_DOUBLE,
                             value='0'),
        ParameterDeclaration(name='__ego_center_z__',
                             parameterType=ParameterType.PARAMETERTYPE_DOUBLE,
                             value='0'),
    ]

    builder = ParameterDeclarationsBuilder(parameterDeclarations=declarations)
    return builder.get_result()
