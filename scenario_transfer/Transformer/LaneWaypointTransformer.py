from typing import Type, TypeVar, List
from enum import Enum

import lanelet2
from lanelet2.core import Lanelet
from lanelet2.projection import UtmProjector

from apollo_msgs.routing_msgs import LaneWaypoint
from openscenario_msgs import (Waypoint, RouteStrategy, Position)

from ..Geometry import Geometry
from .Transformable import Transformable


# properties = [lanelet2.core.Lanelet, lanelet2.projection.UtmProjector]
class LaneWaypointTransformer(Transformable):

    T = LaneWaypoint
    V = Waypoint

    def __init__(self, properties: List = []):
        self.properties = properties

    def transform(self, source: T) -> V:
        pose = source.pose  # PointENU
        lanelet = self.properties[0]
        projector = self.properties[1]

        assert isinstance(
            lanelet,
            Lanelet), "lanelet should be of type lanelet2.core.Lanelet"
        assert isinstance(
            projector, UtmProjector
        ), "projector should be of type lanelet2.projection.UtmProjector"

        if source.pose:
            projected_point = Geometry.project_UTM_to_lanelet(
                projector=projector, pose=pose)
            lane_position = Geometry.lane_position(lanelet=lanelet,
                                                   basic_point=projected_point)
            return Waypoint(
                route_strategy=RouteStrategy.ROUTESTRATEGY_SHORTEST,
                position=Position(lane_position=lane_position))
