from typing import Dict, Tuple
from enum import Enum
from dataclasses import dataclass
import lanelet2
from lanelet2.core import LaneletMap
from lanelet2.projection import MGRSProjector
from modules.common.proto.geometry_pb2 import PointENU
from openscenario_msgs import Position, LanePosition, WorldPosition
from scenario_transformer.transformer import Transformer
from scenario_transformer.tools.geometry import Geometry


@dataclass
class PointENUTransformerConfiguration:
    supported_position: 'PointENUTransformer.SupportedPosition'
    lanelet_map: LaneletMap
    projector: lanelet2.projection.MGRSProjector


class PointENUTransformer(Transformer):
    configuration: PointENUTransformerConfiguration

    class SupportedPosition(Enum):
        Lane = 1
        World = 2

    Source = Tuple[PointENU, float]
    Target = Position

    def __init__(self, configuration: PointENUTransformerConfiguration):
        self.configuration = configuration

    def transform(self, source: Source) -> Target:
        if self.configuration.supported_position == PointENUTransformer.SupportedPosition.Lane:
            return Position(lanePosition=self.transformToLanePosition(source))
        return Position(worldPosition=self.transformToWorldPosition(source))

    def transformToLanePosition(self, source: Source) -> LanePosition:
        lanelet_map = self.configuration.lanelet_map
        projector = self.configuration.projector

        projected_point = Geometry.project_UTM_to_lanelet(projector=projector,
                                                          pose=source[0])
        lanelet = Geometry.find_lanelet(lanelet_map, projected_point)
        # Discard heading value
        lane_position = Geometry.lane_position(lanelet=lanelet,
                                               basic_point=projected_point,
                                               heading=0.0)
        return lane_position

    def transformToWorldPosition(self, source: Source) -> WorldPosition:
        pose = Geometry.utm_to_WGS(pose=source[0])
        # Discard heading value
        return WorldPosition(x=pose.lat, y=pose.lon, z=0)
