from typing import List, Dict, Type, TypeVar
from lanelet2.core import Lanelet, LaneletMap


class VectorMapParser:
    lanelet_map: LaneletMap
    projector: MGRSProjector

    def __init__(sel, vector_map_path: str):
        self.mgrs_Projector = MGRSProjector(origin)
        self.lanelet_map = lanelet2.io.load(vector_map_path, self.mgrs_Projector)

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
