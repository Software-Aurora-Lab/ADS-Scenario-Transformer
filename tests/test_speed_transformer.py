from typing import List, Dict
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles
from ads_scenario_transformer.transformer.speed_transformer import SpeedTransformer, SpeedTransformerConfiguration
from ads_scenario_transformer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel


def group_obstacles(
    obstacles: List[PerceptionObstacles]
) -> Dict[str, List[PerceptionObstacles]]:
    grouped_obstacles = {}
    for perception_obstacles in obstacles:
        for obstacle in perception_obstacles.perception_obstacle:

            if obstacle.id not in grouped_obstacles:
                grouped_obstacles[obstacle.id] = []
            grouped_obstacles[obstacle.id].append(obstacle)
    return grouped_obstacles


def test_speed(sf_doppel_scenario_path):
    obstacles = CyberRecordReader.read_channel(
        source_path=sf_doppel_scenario_path,
        channel=CyberRecordChannel.PERCEPTION_OBSTACLES)

    acts = []
    for id, obstacles in group_obstacles(obstacles).items():
        transformer = SpeedTransformer(
            configuration=SpeedTransformerConfiguration(entity_name="ego"))
        act = transformer.transform(source=obstacles)
        acts.append(act)

    assert acts[-1].maneuverGroups[0].maneuvers[0].events[0].actions[
        0].name == "Not Moving"
    assert acts[-1].maneuverGroups[0].maneuvers[0].events[1].actions[
        0].name == "Increasing"
