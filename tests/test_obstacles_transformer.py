import math
from typing import List
import pytest
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles
from ads_scenario_transformer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel
from ads_scenario_transformer.tools.error import LaneFindingError
from ads_scenario_transformer.transformer.obstacles_transformer import ObstaclesTransformer, ObstaclesTransformerConfiguration


@pytest.fixture
def perception_obstacles(
        borregas_doppel_scenario9_path) -> List[PerceptionObstacles]:
    return CyberRecordReader.read_channel(
        source_path=borregas_doppel_scenario9_path,
        channel=CyberRecordChannel.PERCEPTION_OBSTACLES)


@pytest.fixture
def perception_obstacles10(
        borregas_doppel_scenario10_path) -> List[PerceptionObstacles]:
    return CyberRecordReader.read_channel(
        source_path=borregas_doppel_scenario10_path,
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


def test_obstacle_transformer2(perception_obstacles10, vector_map_parser):

    sceanrio_start_timestamp = perception_obstacles10[0].header.timestamp_sec
    obstacles_transformer = ObstaclesTransformer(
        configuration=ObstaclesTransformerConfiguration(
            sceanrio_start_timestamp=sceanrio_start_timestamp,
            vector_map_parser=vector_map_parser,
            waypoint_frequency_in_sec=5,
            direction_change_detection_threshold=60))

    result = obstacles_transformer.transform(source=perception_obstacles10)
    story = result.stories[3]
    assert story.name == "car_4_id_660467 Story"

    events = story.acts[0].maneuverGroups[0].maneuvers[0].events
    assert events[-1].actions[0].name == "Route car_4_id_660467"

    route_action = events[-1].actions[
        0].privateAction.routingAction.assignRouteAction

    available_lane_id = ["92", "282"]
    for waypoint in route_action.route.waypoints:
        id = waypoint.position.lanePosition.laneId
        if id not in available_lane_id:
            assert False, f"Lane id {id} is not available"
