from typing import List, Dict, Type, TypeVar
import lanelet2
from lanelet2.core import Lanelet, LaneletMap, TrafficSign, TrafficLight
from lanelet2.projection import MGRSProjector
from lanelet2.io import Origin

T = TypeVar('T')


class VectorMapParser:
    lanelet_map: LaneletMap
    projector: MGRSProjector

    def __init__(self, vector_map_path: str):
        origin = Origin(0.0, 0.0, 0.0)
        self.projector = MGRSProjector(origin)
        self.lanelet_map = lanelet2.io.load(vector_map_path, self.projector)

    def get_attributes(self, key: str,
                       attribute_type: Type[T]) -> Dict[int, T]:
        """
        - attribute_key: ['location', 'one_way', 'participant:vehicle', 'speed_limit', 'subtype', 'turn_direction', 'type']
        """
        result = {}
        for lanelet in self.lanelet_map.laneletLayer:
            if key in lanelet.attributes:
                result[lanelet.id] = attribute_type(lanelet.attributes[key])
        return result

    def get_lanelets(self, identifiers: List[int]) -> List[Lanelet]:
        return [
            lanelet for lanelet in self.lanelet_map.laneletLayer
            if lanelet.id in identifiers
        ]

    def get_all_intersections(self) -> Dict[int, str]:
        """
        - return: Dict[lanelet id: turn_direction type]
        """
        return self.get_attributes(key='turn_direction', attribute_type=str)

    def get_all_traffic_lights(self) -> List[TrafficLight]:
        return [
            element for element in self.lanelet_map.regulatoryElementLayer
            if isinstance(element, TrafficLight)
        ]

    def regualtory_element_layer(self):
        return self.lanelet_map.regulatoryElementLayer
