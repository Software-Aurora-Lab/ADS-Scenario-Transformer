from typing import List, Dict
import pytest
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

@pytest.fixture
def obstacle_group(borregas_doppel_scenario9_path) -> List[PerceptionObstacles]:
    obstacles = CyberRecordReader.read_channel(
        source_path=borregas_doppel_scenario9_path,
        channel=CyberRecordChannel.PERCEPTION_OBSTACLES)
    return group_obstacles(obstacles)

@pytest.fixture
def id_dict() -> Dict[int, str]:
    return {
        336869: "car_1_id_336869",
        734981: "car_2_id_734981",
        811421: "car_3_id_811421",
        0: "pedestrian_4",
        1: "pedestrian_5_id_1",
        2: "pedestrian_6_id_2"
    }
    
def test_dynamic(obstacle_group, id_dict):
    key = 734981
    obstacles = obstacle_group[key]
    transformer = SpeedTransformer(
        configuration=SpeedTransformerConfiguration(
            entity_name=id_dict[key]))
    act = transformer.transform(source=obstacles)

    speed_events = act.maneuverGroups[0].maneuvers[0].events

    assert len(speed_events) == 9
    assert speed_events[0].actions[0].name == "Constant"
    assert speed_events[0].actions[0].privateAction.longitudinalAction.speedAction.speedActionTarget.absoluteTargetSpeed.value == 0.0
    assert speed_events[0].startTrigger.conditionGroups[0].conditions[0].byValueCondition.simulationTimeCondition.value == 0.0
    assert speed_events[0].actions[0].privateAction.longitudinalAction.speedAction.speedActionDynamics.value == 2.0

    assert speed_events[1].actions[0].name == "Increasing"
    assert speed_events[1].actions[0].privateAction.longitudinalAction.speedAction.speedActionTarget.absoluteTargetSpeed.value == 8.265406088622584
    assert speed_events[1].startTrigger.conditionGroups[0].conditions[0].byValueCondition.simulationTimeCondition.value == 2.3500218391418457
    assert speed_events[1].actions[0].privateAction.longitudinalAction.speedAction.speedActionDynamics.value == 5.0

    assert speed_events[2].actions[0].name == "Decreasing"
    assert speed_events[2].actions[0].privateAction.longitudinalAction.speedAction.speedActionTarget.absoluteTargetSpeed.value == 0.007580676580131125
    assert speed_events[2].startTrigger.conditionGroups[0].conditions[0].byValueCondition.simulationTimeCondition.value == 8.249866008758545
    assert speed_events[2].actions[0].privateAction.longitudinalAction.speedAction.speedActionDynamics.value == 7.0

def test_stationary(obstacle_group, id_dict):

    key = 336869
    obstacles = obstacle_group[key]
    transformer = SpeedTransformer(
        configuration=SpeedTransformerConfiguration(
            entity_name=id_dict[key]))
    act = transformer.transform(source=obstacles)

    speed_events = act.maneuverGroups[0].maneuvers[0].events

    assert len(speed_events) == 1
    assert speed_events[0].actions[0].name == "Constant"
    assert speed_events[0].actions[0].privateAction.longitudinalAction.speedAction.speedActionTarget.absoluteTargetSpeed.value == 0.0
    assert speed_events[0].startTrigger.conditionGroups[0].conditions[0].byValueCondition.simulationTimeCondition.value == 0.0
    assert speed_events[0].actions[0].privateAction.longitudinalAction.speedAction.speedActionDynamics.value == 31.0

    
def test_constant(obstacle_group, id_dict):

    key = 1
    obstacles = obstacle_group[key]
    transformer = SpeedTransformer(
        configuration=SpeedTransformerConfiguration(
            entity_name=id_dict[key]))
    act = transformer.transform(source=obstacles)
    
    speed_events = act.maneuverGroups[0].maneuvers[0].events
    assert len(speed_events) == 1
    assert speed_events[0].actions[0].name == "Constant"
    assert speed_events[0].actions[0].privateAction.longitudinalAction.speedAction.speedActionTarget.absoluteTargetSpeed.value == 2.8
    assert speed_events[0].startTrigger.conditionGroups[0].conditions[0].byValueCondition.simulationTimeCondition.value == 0.0
    assert speed_events[0].actions[0].privateAction.longitudinalAction.speedAction.speedActionDynamics.value == 31.0
    