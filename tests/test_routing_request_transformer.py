import pytest
from openscenario_msgs import Private, TeleportAction, RoutingAction, AssignRouteAction, ScenarioObject
from ads_scenario_transformer.transformer import RoutingRequestTransformer
from ads_scenario_transformer.transformer.routing_request_transformer import RoutingRequestTransformerConfiguration
from ads_scenario_transformer.builder import EntitiesBuilder
from ads_scenario_transformer.builder.entities_builder import ASTEntityType, ASTEntity
from ads_scenario_transformer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel


@pytest.fixture
def ego_scenario_object() -> ScenarioObject:
    builder = EntitiesBuilder()
    return builder.get_result().scenarioObjects[0]


def assert_proto_type_equal(reflection_type, pb2_type):
    assert str(reflection_type.__class__) == str(pb2_type)


def test_routing_request(vector_map_parser, ego_scenario_object,
                         apollo_map_parser, borregas_doppel_scenario9_path):

    routing_request_transformer = RoutingRequestTransformer(
        configuration=RoutingRequestTransformerConfiguration(
            vector_map_parser=vector_map_parser,
            apollo_map_parser=apollo_map_parser,
            ego_scenario_object=ego_scenario_object,
            reference_points=None))

    routing_requests = CyberRecordReader.read_channel(
        source_path=borregas_doppel_scenario9_path,
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
    assert start_lane_position.offset == 0.0
    assert start_lane_position.s == 35.812947374714085
    assert start_lane_position.orientation.h == 0.0

    assert_proto_type_equal(routing_action.assignRouteAction,
                            AssignRouteAction)

    end_waypoint = routing_action.assignRouteAction.route.waypoints[-1]
    end_lane_position = end_waypoint.position.lanePosition

    assert end_lane_position.laneId == "149"
    assert end_lane_position.offset == 0.0
    assert end_lane_position.s == 26.739416492972932
    assert end_lane_position.orientation.h == 0.0


def test_routing_request_from_response(vector_map_parser,
                                       borregas_doppel_scenario9_path,
                                       ego_scenario_object, apollo_map_parser):
    routing_request_transformer = RoutingRequestTransformer(
        configuration=RoutingRequestTransformerConfiguration(
            vector_map_parser=vector_map_parser,
            apollo_map_parser=apollo_map_parser,
            ego_scenario_object=ego_scenario_object,
            reference_points=None))
    routing_responses = CyberRecordReader.read_channel(
        source_path=borregas_doppel_scenario9_path,
        channel=CyberRecordChannel.ROUTING_RESPONSE)

    routing_response = routing_responses[0]
    routing_request = routing_response.routing_request

    openscenario_private = routing_request_transformer.transform(
        routing_request)

    assert_proto_type_equal(openscenario_private, Private)


def test_find_right_lanelet_within_overlapped_lanelets(
        vector_map_parser, apollo_map_parser,
        borregas_scenorita_scenario23_path, ego_scenario_object):

    localization_poses = CyberRecordReader.read_channel(
        source_path=borregas_scenorita_scenario23_path,
        channel=CyberRecordChannel.LOCALIZATION_POSE)

    routing_responses = CyberRecordReader.read_channel(
        source_path=borregas_scenorita_scenario23_path,
        channel=CyberRecordChannel.ROUTING_RESPONSE)

    routing_request_transformer = RoutingRequestTransformer(
        configuration=RoutingRequestTransformerConfiguration(
            vector_map_parser=vector_map_parser,
            apollo_map_parser=apollo_map_parser,
            ego_scenario_object=ego_scenario_object,
            reference_points=[
                localization_poses[0].pose.position,
                localization_poses[-1].pose.position
            ]))

    routing_request = routing_responses[0].routing_request
    openscenario_private = routing_request_transformer.transform(
        routing_request)
    assert_proto_type_equal(openscenario_private, Private)

    routing_action = openscenario_private.privateActions[-1].routingAction
    assert routing_action.acquirePositionAction.position.lanePosition.laneId == "452"


def test_find_right_lanelet_within_overlapped_lanelets_start_end_same(
        vector_map_parser, apollo_map_parser,
        borregas_scenorita_scenario34_path, ego_scenario_object):

    localization_poses = CyberRecordReader.read_channel(
        source_path=borregas_scenorita_scenario34_path,
        channel=CyberRecordChannel.LOCALIZATION_POSE)

    routing_responses = CyberRecordReader.read_channel(
        source_path=borregas_scenorita_scenario34_path,
        channel=CyberRecordChannel.ROUTING_RESPONSE)

    routing_request_transformer = RoutingRequestTransformer(
        configuration=RoutingRequestTransformerConfiguration(
            vector_map_parser=vector_map_parser,
            apollo_map_parser=apollo_map_parser,
            ego_scenario_object=ego_scenario_object,
            reference_points=[
                localization_poses[0].pose.position,
                localization_poses[0].pose.position
            ]))

    routing_request = routing_responses[0].routing_request
    openscenario_private = routing_request_transformer.transform(
        routing_request)
    assert_proto_type_equal(openscenario_private, Private)

    routing_action = openscenario_private.privateActions[-1].routingAction

    assert routing_action.acquirePositionAction.position.lanePosition.laneId == "210"
