from typing import Dict, Tuple
from enum import Enum

import lanelet2

from apollo_msgs.basic_msgs import PointENU
from openscenario_msgs import Position, LanePosition, WorldPosition

from .transformer import Transformer
from ..geometry import Geometry


# properties = ["supported_position": PointENUTransformer.SupportedPosition, "lanelet_map": lanelet2.core.LaneletMap, "projector": lanelet2.projection.UtmProjector]
class PointENUTransformer(Transformer):

    class SupportedPosition(Enum):
        Lane = 1
        World = 2

    Source = Tuple[PointENU, float]
    Target = Position

    def __init__(self, properties: Dict = {}):
        self.properties = properties

    def transform(self, source: Source) -> Target:
        if self.properties["supported_position"] == PointENUTransformer.SupportedPosition.Lane:
            return Position(lane_position=self.transformToLanePosition(source))
        return Position(world_position=self.transformToWorldPosition(source))

    def transformToLanePosition(self, source: Source) -> LanePosition:
        lanelet_map = self.properties["lanelet_map"]
        projector = self.properties["projector"]

        assert isinstance(
            lanelet_map, lanelet2.core.LaneletMap
        ), "lanelet_map should be of type lanelet2.core.LaneletMap"
        assert isinstance(
            projector, lanelet2.projection.UtmProjector
        ), "projector should be of type lanelet2.projection.UtmProjector"

        projected_point = Geometry.project_UTM_to_lanelet(projector=projector,
                                                          pose=source[0])
        lanelet = Geometry.find_lanelet(lanelet_map, projected_point)
        lane_position = Geometry.lane_position(lanelet=lanelet,
                                               basic_point=projected_point,
                                               heading=source[1])
        return lane_position

    def transformToWorldPosition(self, source: Source) -> WorldPosition:
        pose = Geometry.utm_to_WGS(pose=source[0])
        return WorldPosition(x=pose.lat, y=pose.lon, z=0, h=source[1])
