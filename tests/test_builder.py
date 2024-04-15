import pytest
from datetime import datetime
from openscenario_msgs import CatalogDefinition, FileHeader, Entities, ParameterDeclarations, ParameterDeclaration, ScenarioDefinition, Private, ScenarioObject, TeleportAction, RoutingAction
from scenario_transformer.builder import CatalogDefinitionBuilder, FileHeaderBuilder, EntitiesBuilder, ParameterDeclarationsBuilder, RoadNetworkBuilder, TrafficSignalControllerBuilder, TrafficSignalStateBuilder, ScenarioDefinitionBuilder
from scenario_transformer.builder.private_builder import PrivateBuilder
from scenario_transformer.builder.entities_builder import EntityType


def test_entities_builder():
    builder = EntitiesBuilder(entities=[
        EntityType.NPC, EntityType.NPC, EntityType.EGO, EntityType.PEDESTRIAN,
        EntityType.NPC
    ])

    builder.add_default_entity(EntityType.NPC)

    entities = builder.get_result()
    assert isinstance(entities, Entities)
    assert len(entities.scenarioObjects) == 6

    assert entities.scenarioObjects[0].name == "ego"
    assert entities.scenarioObjects[1].name == "npc_1"
    assert entities.scenarioObjects[2].name == "npc_2"
    assert entities.scenarioObjects[3].name == "npc_3"
    assert entities.scenarioObjects[4].name == "pedestrian_4"
    assert entities.scenarioObjects[5].name == "npc_5"


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
    controller_builder = TrafficSignalControllerBuilder(name="StraghtSignal")
    state_builder = TrafficSignalStateBuilder(
        id_states=[('12515',
                    "red;solidOn;circle"), ('12504', "red;solidOn;circle")])
    controller_builder.add_phase(name="RED", states=state_builder.get_result())

    state_builder = TrafficSignalStateBuilder(
        id_states=[('12515',
                    "green;solidOn;circle"), ('12504',
                                              "green;solidOn;circle")])

    controller_builder.add_phase(name="RED", states=state_builder.get_result())

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


def test_scenario_definition_builder(storyboard):
    parameter_declarations = [
        ParameterDeclaration(name="__ego_dimensions_length__",
                             parameterType=2,
                             value='0'),
        ParameterDeclaration(name="__ego_dimensions_width__",
                             parameterType=2,
                             value='0')
    ]

    builder = ScenarioDefinitionBuilder(
        parameter_declarations=parameter_declarations)

    builder.make_road_network(lanelet_map_path="lanelet_map.osm")
    builder.make_default_entities(entities=[
        EntityType.EGO, EntityType.NPC, EntityType.NPC, EntityType.PEDESTRIAN
    ])
    builder.make_storyboard(storyboard=storyboard)
    scenario_definition = builder.get_result()

    assert isinstance(scenario_definition, ScenarioDefinition)
    assert scenario_definition.roadNetwork is not None
    assert scenario_definition.catalogLocations is not None
    assert scenario_definition.entities is not None
    assert scenario_definition.storyboard is not None


def test_private_builder(waypoints):

    entities_builder = EntitiesBuilder(entities=[EntityType.EGO])
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
