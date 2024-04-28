import pytest
from datetime import datetime
from typing import List
from openscenario_msgs import CatalogDefinition, FileHeader, Entities, ParameterDeclarations, ParameterDeclaration, ScenarioDefinition, Private, ScenarioObject, TeleportAction, RoutingAction
from scenario_transformer.builder import CatalogDefinitionBuilder, FileHeaderBuilder, EntitiesBuilder, ParameterDeclarationsBuilder, RoadNetworkBuilder, ScenarioDefinitionBuilder
from scenario_transformer.builder.private_builder import PrivateBuilder
from scenario_transformer.builder.entities_builder import ASTEntityType, ASTEntity
from scenario_transformer.builder.traffic_signal_controller_builder import TrafficSignalControllerBuilder, PhaseBuilder, TrafficSignalStateBuilder, TrafficLightbulbState


@pytest.fixture
def ast_entity() -> List[ASTEntity]:

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


def test_entities_builder(ast_entities):
    builder = EntitiesBuilder()
    for ast_entity in ast_entities:
        builder.add_entity(ast_entity)

    entities = builder.get_result()
    assert isinstance(entities, Entities)
    assert len(entities.scenarioObjects) == 5

    assert entities.scenarioObjects[0].name == "ego"
    assert entities.scenarioObjects[1].name == "car_1"
    assert entities.scenarioObjects[2].name == "car_2_id_100"
    assert entities.scenarioObjects[3].name == "pedestrian_3_id_200"
    assert entities.scenarioObjects[4].name == "car_4_id_300"


def test_file_header_builder():
    builder = FileHeaderBuilder()
    file_header = builder.get_result()
    assert isinstance(file_header, FileHeader)

    expected_format = '%Y-%m-%dT%H:%M:%S'
    try:
        datetime.strptime(file_header.date, expected_format)
    except ValueError:
        pytest.fail(f"Date format should be {expected_format}")
    assert file_header.description == "Scenario Generated by ADS Scenario Tranformer"
    assert file_header.author == "ADS Scenario Tranformer"


def test_catalog_definition_builder():
    builder = CatalogDefinitionBuilder()
    catalog_definition = builder.get_result()
    assert isinstance(catalog_definition, CatalogDefinition)


def test_parameter_declarations_builder():

    declarations = [
        ParameterDeclaration(name="__ego_dimensions_length__",
                             parameterType=2,
                             value='0'),
        ParameterDeclaration(name="__ego_dimensions_width__",
                             parameterType=2,
                             value='0')
    ]

    builder = ParameterDeclarationsBuilder(parameterDeclarations=declarations)
    parameter_declarations = builder.get_result()
    assert isinstance(parameter_declarations, ParameterDeclarations)
    assert len(parameter_declarations.parameterDeclarations) == 2


def test_road_network_builder():

    state_builder = TrafficSignalStateBuilder()
    state_builder.make_state(id='12515',
                             state=TrafficLightbulbState.RED_ON_CIRCLE)

    phase_builder = PhaseBuilder(name="RED")
    phase_builder.add_state(state=state_builder.get_result())

    controller_builder = TrafficSignalControllerBuilder(name="StraghtSignal")
    controller_builder.add_phase(phase_builder.get_result())

    state_builder = TrafficSignalStateBuilder()
    state_builder.make_state(id='12515',
                             state=TrafficLightbulbState.GREEN_ON_CIRCLE)
    phase_builder = PhaseBuilder(name="GREEN")
    phase_builder.add_state(state=state_builder.get_result())
    controller_builder.add_phase(phase_builder.get_result())

    builder = RoadNetworkBuilder(
        lanelet_map_path="/home/users/lanelet_map.osm",
        trafficSignalControllers=[controller_builder.get_result()])

    road_network = builder.get_result()

    assert road_network.logicFile.filepath == "/home/users/lanelet_map.osm"
    assert len(road_network.trafficSignals.trafficSignalControllers) == 1

    traffic_signal = road_network.trafficSignals.trafficSignalControllers[0]

    assert len(traffic_signal.phases) == 2
    assert traffic_signal.phases[0].name == "RED"
    assert traffic_signal.phases[1].trafficSignalStates[
        0].trafficSignalId == "12515"


def test_scenario_definition_builder(storyboard, ast_entities):
    parameter_declarations = [
        ParameterDeclaration(name="__ego_dimensions_length__",
                             parameterType=2,
                             value='0'),
        ParameterDeclaration(name="__ego_dimensions_width__",
                             parameterType=2,
                             value='0')
    ]

    entities_builder = EntitiesBuilder()
    for ast_entity in ast_entities:
        entities_builder.add_default_entity(ast_entity)

    builder = ScenarioDefinitionBuilder(
        parameter_declarations=parameter_declarations)

    builder.make_road_network(lanelet_map_path="lanelet_map.osm")
    builder.make_entities(entities=entities_builder.get_result())
    builder.make_storyboard(storyboard=storyboard)
    scenario_definition = builder.get_result()

    assert isinstance(scenario_definition, ScenarioDefinition)
    assert scenario_definition.roadNetwork is not None
    assert scenario_definition.catalogLocations is not None
    assert scenario_definition.entities is not None
    assert scenario_definition.storyboard is not None


def test_private_builder(waypoints):

    entities_builder = EntitiesBuilder()
    ego = entities_builder.get_result().scenarioObjects[0]

    assert_proto_type_equal(ego, ScenarioObject)

    private_builder = PrivateBuilder(scenario_object=ego)
    private_builder.make_routing_action_with_teleport_action(
        waypoints=waypoints,
        closed=False,
        name="Routing Request Transformer Generated Route")

    openscenario_private = private_builder.get_result()

    assert isinstance(openscenario_private,
                      Private), "The private should be of type Private"
    assert openscenario_private.entityRef == "ego"

    teleport_action = openscenario_private.privateActions[0].teleportAction
    routing_action = openscenario_private.privateActions[1].routingAction
    assert_proto_type_equal(teleport_action, TeleportAction)
    assert_proto_type_equal(routing_action, RoutingAction)

    start_lane_position = teleport_action.position.lanePosition
    assert start_lane_position.laneId == "22"
    assert start_lane_position.offset == 0.1750399287494411
    assert start_lane_position.s == 35.714714923990464
    assert start_lane_position.orientation.h == 2.883901414579166

    end_waypoint = routing_action.assignRouteAction.route.waypoints[-1]
    end_lane_position = end_waypoint.position.lanePosition

    assert end_lane_position.laneId == "149"
    assert end_lane_position.offset == 1.4604610803960605
    assert end_lane_position.s == 26.739416492972932
    assert end_lane_position.orientation.h == -1.9883158777364047


def assert_proto_type_equal(reflection_type, pb2_type):
    assert str(reflection_type.__class__) == str(pb2_type)
