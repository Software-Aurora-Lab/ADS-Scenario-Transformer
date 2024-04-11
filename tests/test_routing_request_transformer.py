import pytest
import unittest
import lanelet2
from lanelet2.projection import MGRSProjector
from lanelet2.io import Origin
from openscenario_msgs import Private, TeleportAction, RoutingAction, AssignRouteAction, ScenarioObject
from scenario_transfer.transformer import RoutingRequestTransformer
from scenario_transfer.transformer.routing_request_transformer import RoutingRequestTransformerConfiguration
from scenario_transfer.builder import EntitiesBuilder
from scenario_transfer.builder.entities_builder import EntityType
from scenario_transfer.openscenario import OpenScenarioEncoder
from scenario_transfer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel


@pytest.fixture
def ego_scenario_object() -> ScenarioObject:
    builder = EntitiesBuilder(entities=[EntityType.EGO])
    return builder.get_result().scenarioObjects[0]


def assert_proto_type_equal(reflection_type, pb2_type):
    assert str(reflection_type.__class__) == str(pb2_type)


def test_routing_request(lanelet_map, mgrs_projector, ego_scenario_object,
                         apollo_map_parser, borregas_apollo_scenario9_path):

    routing_request_transformer = RoutingRequestTransformer(
        configuration=RoutingRequestTransformerConfiguration(
            lanelet_map=lanelet_map,
            projector=mgrs_projector,
            apollo_map_parser=apollo_map_parser,
            ego_scenario_object=ego_scenario_object))

    routing_requests = CyberRecordReader.read_channel(
        source_path=borregas_apollo_scenario9_path,
        channel=CyberRecordChannel.ROUTING_REQUEST)

    routing_request = routing_requests[0]
    openscenario_private = routing_request_transformer.transform(
        routing_request)

    assert_proto_type_equal(openscenario_private, Private)
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

    assert_proto_type_equal(routing_action.assignRouteAction,
                            AssignRouteAction)

    end_waypoint = routing_action.assignRouteAction.route.waypoints[-1]
    end_lane_position = end_waypoint.position.lanePosition

    assert end_lane_position.laneId == "149"
    assert end_lane_position.offset == 1.4604610803960605
    assert end_lane_position.s == 26.739416492972932
    assert end_lane_position.orientation.h == -1.9883158777364047


def test_routing_request_from_response(lanelet_map, mgrs_projector,
                                       ego_scenario_object, apollo_map_parser):
    routing_request_transformer = RoutingRequestTransformer(
        configuration=RoutingRequestTransformerConfiguration(
            lanelet_map=lanelet_map,
            projector=mgrs_projector,
            apollo_map_parser=apollo_map_parser,
            ego_scenario_object=ego_scenario_object))
    routing_responses = CyberRecordReader.read_channel(
        source_path="./samples/apollo_borregas/00000035.00000",
        channel=CyberRecordChannel.ROUTING_RESPONSE)

    routing_response = routing_responses[0]
    routing_request = routing_response.routing_request

    openscenario_private = routing_request_transformer.transform(
        routing_request)

    assert_proto_type_equal(openscenario_private, Private)
