from enum import Enum
from typing import Tuple
from pathlib import Path
from apollo_msgs import Map, PointENU
from pkgs.scenorita.map_service import MapService


class ApolloMapService:
    map_service: MapService

    def __init__(self) -> None:
        self.map_service = MapService()

    def load_map_from_file(self, filename: str):
        self.map_service.load_map_from_file(filename)

    def load_map_from_proto(self, map: Map):
        self.map_service.load_map_from_proto(map)

    def get_lane_coord_and_heading(self, lane_id: str,
                                   s: float) -> Tuple[PointENU, float]:
        return self.map_service.get_lane_coord_and_heading(lane_id=lane_id,
                                                           s=s)