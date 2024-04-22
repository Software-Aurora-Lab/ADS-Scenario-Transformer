from typing import Dict
from lanelet2.core import TrafficLight
from modules.map.proto.map_signal_pb2 import Signal
from scenario_transformer.tools.geometry import Geometry
from scenario_transformer.tools.apollo_map_parser import ApolloMapParser
from scenario_transformer.tools.vector_map_parser import VectorMapParser


class TrafficSignalMapper:
    apollo_map_parser: ApolloMapParser
    vector_map_parser: VectorMapParser

    def __init__(self, apollo_map_parser: ApolloMapParser,
                 vector_map_parser: VectorMapParser):
        self.apollo_map_parser = apollo_map_parser
        self.vector_map_parser = vector_map_parser
        self.traffic_light_id_map = self.map_traffic_light_id_using_coordinate(
        )

    def map_traffic_light_id_using_coordinate(self) -> Dict[str, TrafficLight]:
        """
        - Map Apollo HD map signals and Autoware Vector map traffic lights.
        """
        traffic_light_mapping = {}
        for signal_id in self.apollo_map_parser.get_signals():
            signal = self.apollo_map_parser.get_signal_by_id(signal_id)

            if signal.type == Signal.MIX_2_HORIZONTAL or signal.type == Signal.MIX_2_VERTICAL or signal.type == Signal.MIX_3_HORIZONTAL or signal.type == Signal.MIX_3_VERTICAL:

                nearest_traffic_light = Geometry.find_nearest_traffic_light(
                    map=self.vector_map_parser.lanelet_map,
                    signal=signal,
                    projector=self.vector_map_parser.projector)
                if nearest_traffic_light:
                    traffic_light_mapping[signal_id] = nearest_traffic_light
                else:
                    print(
                        f"Warning: signal_id: {signal_id} cannot be mapped to a traffic light"
                    )

        return traffic_light_mapping
