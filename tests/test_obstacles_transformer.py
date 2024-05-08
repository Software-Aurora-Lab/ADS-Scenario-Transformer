import math
from typing import List
import pytest
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles
from ads_scenario_transformer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel
from ads_scenario_transformer.transformer.obstacles_transformer import ObstaclesTransformer, ObstaclesTransformerConfiguration


@pytest.fixture
def perception_obstacles(
        borregas_doppel_scenario9_path) -> List[PerceptionObstacles]:
    return CyberRecordReader.read_channel(
        source_path=borregas_doppel_scenario9_path,
        channel=CyberRecordChannel.PERCEPTION_OBSTACLES)


def test_obstacle_transformer(perception_obstacles, vector_map_parser):

    sceanrio_start_timestamp = perception_obstacles[0].header.timestamp_sec
    obstacles_transformer = ObstaclesTransformer(
        configuration=ObstaclesTransformerConfiguration(
            sceanrio_start_timestamp=sceanrio_start_timestamp,
            vector_map_parser=vector_map_parser,
            waypoint_frequency_in_sec=1,
            direction_change_detection_threshold=60))

    result = obstacles_transformer.transform(source=perception_obstacles)

    assert len(result.entities_with_id) == 7
    assert len(result.stories) == 6

    pedestrian5_events = result.stories[-1].acts[0].maneuverGroups[
        0].maneuvers[0].events

    assert pedestrian5_events[0].actions[
        0].name == "Locate pedestrian_6_id_2 on the road"
    assert pedestrian5_events[1].actions[-1].name == "Route pedestrian_6_id_2"
    assert len(pedestrian5_events[1].actions[-1].privateAction.routingAction.
               assignRouteAction.route.waypoints) == 31
