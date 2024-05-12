from typing import List, Dict, Type, TypeVar
from lanelet2.core import Lanelet, LaneletMap
from lanelet2_extension_python.projection import MGRSProjector
from src.tools.utils import construct_lane_boundary_linestring


class VectorMapParser:
    _instance = None
    lanelet_map: LaneletMap
    projector: MGRSProjector 

    T = TypeVar('T')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def __init__(self):
        raise RuntimeError('Call instance() instead')
      
    def get_attributes(self, key: str, attribute_type: Type[T]) -> Dict[int, T]:
        """
        - attribute_key: ['location', 'one_way', 'participant:vehicle', 'speed_limit', 'subtype', 'turn_direction', 'type']
        """
        result = {}
        for lanelet in self.lanelet_map.laneletLayer:
            if key in lanelet.attributes:
                result[lanelet.id] = attribute_type(lanelet.attributes[key])
        return result

    def get_lanelets(self, identifiers: List[int]) -> List[Lanelet]:
        return [lanelet for lanelet in self.lanelet_map.laneletLayer if lanelet.id in identifiers]

    def get_all_intersections(self) -> Dict[int, str]:
        """
        - return: Dict[lanelet id: turn_direction type]
        """
        return self.get_attributes(key='turn_direction', attribute_type=str)

    def get_lane_boundaries(self) -> dict:
        boundaries = dict()
        for lane in self.lanelet_map.laneletLayer:
            lane_id = lane.id
            l, r = construct_lane_boundary_linestring(lane)
            boundaries[f'{lane_id}_L'] = l
            boundaries[f'{lane_id}_R'] = r
        return boundaries
