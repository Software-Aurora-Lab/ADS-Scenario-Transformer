from typing import List
from enum import Enum

import lanelet2

from apollo_msgs.basic_msgs import PointENU
from openscenario_msgs import Position, LanePosition, WorldPosition

from .Transformer import Transformer
from ..Geometry import Geometry


# properties = [PointENUTransformer.SupportedPosition, lanelet2.core.LaneletMap, lanelet2.projection.UtmProjector]
class PointENUTransformer(Transformer):

    class SupportedPosition(Enum):
        Lane = 1
        World = 2

    Source = PointENU
    Target = Position

    def __init__(self, properties: List = []):
        self.properties = properties

    def transform(self, source: T) -> V:
        if self.properties[0] == PointENUTransformer.SupportedPosition.Lane:
            return Position(lane_position=self.transformToLanePosition(source))
        return Position(world_position=self.transformToWorldPosition(source))

    def transformToLanePosition(self, source: T) -> LanePosition:
        lanelet_map = self.properties[1]
        projector = self.properties[2]

        assert isinstance(
            lanelet_map, lanelet2.core.LaneletMap
        ), "lanelet_map should be of type lanelet2.core.LaneletMap"
        assert isinstance(
            projector, lanelet2.projection.UtmProjector
        ), "projector should be of type lanelet2.projection.UtmProjector"

        projected_point = Geometry.project_UTM_to_lanelet(projector=projector,
                                                          pose=source)
        lanelet = Geometry.find_lanelet(lanelet_map, projected_point)
        lane_position = Geometry.lane_position(lanelet=lanelet,
                                               basic_point=projected_point)
        return lane_position

    def transformToWorldPosition(self, source: T) -> WorldPosition:
        pose = Geometry.utm_to_WGS(pose=source)
        return WorldPosition(x=pose.lat, y=pose.lon, z=0)
