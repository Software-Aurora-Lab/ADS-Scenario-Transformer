from typing import Dict, Tuple
import math
from lanelet2.core import LaneletMap
from lanelet2.projection import MGRSProjector
from modules.common.proto.geometry_pb2 import PointENU
from modules.routing.proto.routing_pb2 import LaneWaypoint
from openscenario_msgs import (Waypoint, RouteStrategy)
from scenario_transfer.transformer import Transformer
from scenario_transfer.transformer.pointenu_transformer import PointENUTransformer
from scenario_transfer.tools.apollo_map_service import ApolloMapService


class LaneWaypointTransformer(Transformer):
    """
    - properties = [
        "lanelet_map": lanelet2.core.LaneletMap, 
        "projector": lanelet2.projection.MGRSProjector, 
        "apollo_map_service": tools.apollo_map_service.ApolloMapService
    ]
    """
    Source = LaneWaypoint
    Target = Waypoint

    def __init__(self, properties: Dict = {}):
        self.properties = properties

    def transform(self, source: Source) -> Target:
        pose = source.pose
        heading = source.heading if source.heading else 0.0

        if math.isnan(
                pose.x
        ):  # if pose.x and pose.y are nan, then it will check laneId and s
            (pose, heading) = self.get_pose_from_apollo_waypoint(source)

        lanelet_map = self.properties["lanelet_map"]
        projector = self.properties["projector"]

        assert isinstance(
            lanelet_map,
            LaneletMap), "lanelet should be of type lanelet2.core.Lanelet"
        assert isinstance(
            projector, MGRSProjector
        ), "projector should be of type lanelet2.projection.MGRSProjector"

        pointenu_transformer = PointENUTransformer(
            properties={
                "supported_position":
                PointENUTransformer.SupportedPosition.Lane,
                "lanelet_map": lanelet_map,
                "projector": projector
            })
        position = pointenu_transformer.transform((pose, heading))

        return Waypoint(routeStrategy=RouteStrategy.ROUTESTRATEGY_SHORTEST,
                        position=position)

    def get_pose_from_apollo_waypoint(
            self, source: Source) -> Tuple[PointENU, float]:
        apollo_map_service = self.properties["apollo_map_service"]

        assert isinstance(
            apollo_map_service, ApolloMapService
        ), "apollo_map_service should be of type ApolloMapService"

        (point, heading) = apollo_map_service.get_lane_coord_and_heading(
            lane_id=source.id, s=source.s)
        return (PointENU(x=point.x, y=point.y, z=0), heading)
