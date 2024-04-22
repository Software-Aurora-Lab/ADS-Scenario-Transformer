import math
from typing import List, Dict
from dataclasses import dataclass
from collections import defaultdict
from modules.perception.proto.traffic_light_detection_pb2 import TrafficLightDetection, TrafficLight
from openscenario_msgs import TrafficSignalController, Phase
from scenario_transformer.transformer import Transformer
from scenario_transformer.tools.apollo_map_parser import ApolloMapParser
from scenario_transformer.tools.vector_map_parser import VectorMapParser
from scenario_transformer.tools.traffic_signal_mapper import TrafficSignalMapper
from scenario_transformer.builder.traffic_signal_controller_builder import TrafficSignalControllerBuilder, PhaseBuilder, TrafficSignalStateBuilder, TrafficLightbulbState


@dataclass
class TrafficSignalTransformerConfiguration:
    apollo_map_parser: ApolloMapParser
    vector_map_parser: VectorMapParser


@dataclass
class TrafficSignalTransformerResult:
    road_network_traffic: List[TrafficSignalController]


class TrafficSignalTransformer(Transformer):
    traffic_signal_mapper: TrafficSignalMapper
    configuration: TrafficSignalTransformerConfiguration

    Source = List[TrafficLightDetection]
    Target = TrafficSignalTransformerResult

    def __init__(self, configuration: TrafficSignalTransformerConfiguration):
        self.configuration = configuration
        self.traffic_signal_mapper = TrafficSignalMapper(
            apollo_map_parser=self.configuration.apollo_map_parser,
            vector_map_parser=self.configuration.vector_map_parser)

    def transform(self, source: Source) -> Target:
        traffic_phases = self.create_traffic_phases(
            traffic_light_detections=source)

        road_network_controllers = []
        for id, phases in traffic_phases.items():
            traffic_signal_controller_builder = TrafficSignalControllerBuilder(
                name=f"TrafficSignalGroup {id}", phases=phases)
            traffic_signal_controller = traffic_signal_controller_builder.get_result(
            )
            road_network_controllers.append(traffic_signal_controller)

        return TrafficSignalTransformerResult(
            road_network_traffic=road_network_controllers)

    def create_traffic_phases(
        self, traffic_light_detections: List[TrafficLightDetection]
    ) -> Dict[str, List[Phase]]:
        """
        Create Traffic phases per traffic light id.
        """

        signal_states = defaultdict(list)
        for traffic_light_detection in traffic_light_detections:
            timestamp_sec = traffic_light_detection.header.timestamp_sec
            for signal in traffic_light_detection.traffic_light:
                signal_states[signal.id].append((signal, timestamp_sec))

        traffic_light_states = defaultdict(list)
        for signal_id, signal_states in signal_states.items():
            traffic_light = self.traffic_signal_mapper.traffic_light_id_map[
                signal_id]
            if traffic_light.id not in traffic_light_states:
                traffic_light_states[traffic_light.id] = signal_states

        traffic_phases = defaultdict(list)
        for traffic_light_id, signal_states in traffic_light_states.items():
            phases = []
            start_color = None
            start_timestamp = None
            for idx, (signal, timestamp) in enumerate(signal_states):
                if not start_color:
                    start_color = signal.color
                    start_timestamp = timestamp
                    continue

                if start_color != signal.color or idx == len(
                        signal_states) - 1:
                    duration = math.floor(timestamp - start_timestamp)

                    phases.append(
                        self.create_phase(
                            traffic_light_id=str(traffic_light_id),
                            color=start_color,
                            duration=duration))
                    start_color = signal.color
                    start_timestamp = timestamp

            traffic_phases[traffic_light_id] = phases

        return traffic_phases

    def create_phase(self, traffic_light_id: str, color: TrafficLight.Color,
                     duration: float) -> Phase:

        color_state = None
        if color == TrafficLight.Color.RED:
            color_state = TrafficLightbulbState.RED_ON_CIRCLE
        elif color == TrafficLight.Color.YELLOW:
            color_state = TrafficLightbulbState.YELLOW_ON_CIRCLE
        elif color == TrafficLight.Color.GREEN:
            color_state = TrafficLightbulbState.GREEN_ON_CIRCLE
        else:
            # default color_state is GREEN_ON_CIRCLE
            color_state = TrafficLightbulbState.GREEN_ON_CIRCLE

        state_builder = TrafficSignalStateBuilder()
        state_builder.make_state(id=traffic_light_id, state=color_state)
        traffic_signal_state = state_builder.get_result()
        phase_builder = PhaseBuilder(name="", duration=duration)
        phase_builder.add_state(state=traffic_signal_state)
        return phase_builder.get_result()
