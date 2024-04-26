from typing import List
import pytest
from modules.perception.proto.traffic_light_detection_pb2 import TrafficLightDetection, TrafficLight
from scenario_transformer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel
from scenario_transformer.transformer.traffic_signal_transformer import TrafficSignalTransformer, TrafficSignalTransformerConfiguration, TrafficSignalTransformerResult


@pytest.fixture
def traffic_light_detections(
        borregas_doppel_scenario9_path) -> List[TrafficLightDetection]:

    return CyberRecordReader.read_channel(
        source_path=borregas_doppel_scenario9_path,
        channel=CyberRecordChannel.TRAFFIC_LIGHT)


def test_traffic_signal_transformer(traffic_light_detections,
                                    vector_map_parser, apollo_map_parser):

    traffic_signal_transformer = TrafficSignalTransformer(
        configuration=TrafficSignalTransformerConfiguration(
            vector_map_parser=vector_map_parser,
            apollo_map_parser=apollo_map_parser))

    result = traffic_signal_transformer.transform(traffic_light_detections)

    traffic_signal_controllers = result.road_network_traffic
    assert len(traffic_signal_controllers) == 4
    assert traffic_signal_controllers[0].name == "TrafficSignalGroup 520"
    assert len(traffic_signal_controllers[0].phases) == 3
    assert traffic_signal_controllers[1].name == "TrafficSignalGroup 494"
    assert len(traffic_signal_controllers[1].phases) == 2
    assert traffic_signal_controllers[2].name == "TrafficSignalGroup 586"
    assert len(traffic_signal_controllers[2].phases) == 1
    assert traffic_signal_controllers[3].name == "TrafficSignalGroup 553"
    assert len(traffic_signal_controllers[3].phases) == 1
