from ads_scenario_transformer.transformer.localization_transformer import LocalizationTransformer, LocalizationTransformerConfiguration
import pytest
from openscenario_msgs import Private, TeleportAction, RoutingAction, AssignRouteAction, ScenarioObject
from ads_scenario_transformer.transformer import RoutingRequestTransformer
from ads_scenario_transformer.transformer.routing_request_transformer import RoutingRequestTransformerConfiguration

from ads_scenario_transformer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel


def assert_proto_type_equal(reflection_type, pb2_type):
    assert str(reflection_type.__class__) == str(pb2_type)


def test_localization_find_right_lanelet_within_overlapped_lanelets(
        vector_map_parser, apollo_map_parser,
        borregas_scenorita_scenario140_path, entities):

    localization_poses = CyberRecordReader.read_channel(
        source_path=borregas_scenorita_scenario140_path,
        channel=CyberRecordChannel.LOCALIZATION_POSE)

    localization_transformer = LocalizationTransformer(
        configuration=LocalizationTransformerConfiguration(
            vector_map_parser=vector_map_parser,
            apollo_map_parser=apollo_map_parser,
            ego_scenario_object=entities.scenarioObjects[0]))

    openscenario_private = localization_transformer.transform(
        localization_poses)
    assert_proto_type_equal(openscenario_private, Private)

    routing_action = openscenario_private.privateActions[-1].routingAction
    assert routing_action.acquirePositionAction.position.lanePosition.laneId == "137"
