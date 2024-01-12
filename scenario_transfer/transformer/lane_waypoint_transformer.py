from typing import Dict

import lanelet2
from lanelet2.core import Lanelet
from lanelet2.projection import UtmProjector

from apollo_msgs import Map as ApolloHDMap
from apollo_msgs.routing_msgs import LaneWaypoint
from openscenario_msgs import (Waypoint, RouteStrategy, Position)
from pkgs.scenorita.map_service import MapService

from .transformer import Transformer
from ..geometry import Geometry
from scenario_transfer.apollo_map_io_handler import ApolloMapIOHandler

# properties = ["lanelet": lanelet2.core.Lanelet, "projector": lanelet2.projection.UtmProjector, "apollo_map": apollo_msgs.Map]
class LaneWaypointTransformer(Transformer):

    Source = LaneWaypoint
    Target = Waypoint

    def __init__(self, properties: Dict = {}):
        self.properties = properties

    def transform(self, source: Source) -> Target:
        pose = source.pose  # PointENU
        
        if source.pose:
            lanelet = self.properties["lanelet"]
            projector = self.properties["projector"]

            assert isinstance(
                lanelet,
                Lanelet), "lanelet should be of type lanelet2.core.Lanelet"
            assert isinstance(
                projector, UtmProjector
            ), "projector should be of type lanelet2.projection.UtmProjector"
            
            projected_point = Geometry.project_UTM_to_lanelet(
                projector=projector, pose=pose)
            lane_position = Geometry.lane_position(lanelet=lanelet,
                                                   basic_point=projected_point,
                                                   heading=source.heading)
            return Waypoint(
                route_strategy=RouteStrategy.ROUTESTRATEGY_SHORTEST,
                position=Position(lane_position=lane_position))