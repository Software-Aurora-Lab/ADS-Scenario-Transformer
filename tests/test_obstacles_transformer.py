import math
from typing import List
import pytest
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles
from scenario_transformer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel
from scenario_transformer.transformer.obstacles_transformer import ObstaclesTransformer, ObstaclesTransformerConfiguration


@pytest.fixture
def perception_obstacles(
        borregas_doople_scenario9_path) -> List[PerceptionObstacles]:
    return CyberRecordReader.read_channel(
        source_path=borregas_doople_scenario9_path,
        channel=CyberRecordChannel.PERCEPTION_OBSTACLES)


def test_obstacle_transformer(perception_obstacles, vector_map_parser):

    sceanrio_start_timestamp = perception_obstacles[0].header.timestamp_sec
    obstacles_transformer = ObstaclesTransformer(
        configuration=ObstaclesTransformerConfiguration(
            sceanrio_start_timestamp=sceanrio_start_timestamp,
            lanelet_map=vector_map_parser.lanelet_map,
            projector=vector_map_parser.projector))

    result = obstacles_transformer.transform(source=perception_obstacles)

    assert len(result.entities_with_id) == 6
    assert len(result.stories) == 6
