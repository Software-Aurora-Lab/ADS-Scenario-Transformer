from typing import Dict, Tuple
import math

from lanelet2.core import LaneletMap
from lanelet2.projection import UtmProjector

from apollo_msgs import (Map as ApolloHDMap, PointENU, LaneWaypoint)
from openscenario_msgs import (Waypoint, RouteStrategy)
from pkgs.scenorita.map_service import MapService

from scenario_transfer.transformer import Transformer
from scenario_transfer.transformer.pointenu_transformer import PointENUTransformer


# properties = ["lanelet_map": lanelet2.core.LaneletMap, "projector": lanelet2.projection.UtmProjector, "apollo_map": apollo_msgs.Map]
class LaneWaypointTransformer(Transformer):

    Source = LaneWaypoint
    Target = Waypoint

    def __init__(self, properties: Dict = {}):
        self.properties = properties

    def transform(self, source: Source) -> Target:
        pose = source.pose
        heading = source.heading if source.heading else 0.0

        if math.isnan(
                pose.x
        ):  # if pose.x and pose.y are nan, then it will check lane_id and s
            (pose, heading) = self.get_pose_from_apollo_waypoint(source)

        lanelet_map = self.properties["lanelet_map"]
        projector = self.properties["projector"]

        assert isinstance(
            lanelet_map,
            LaneletMap), "lanelet should be of type lanelet2.core.Lanelet"
        assert isinstance(
            projector, UtmProjector
        ), "projector should be of type lanelet2.projection.UtmProjector"

        pointenu_transformer = PointENUTransformer(
            properties={
                "supported_position":
                PointENUTransformer.SupportedPosition.Lane,
                "lanelet_map": lanelet_map,
                "projector": projector
            })
        position = pointenu_transformer.transform((pose, heading))

        return Waypoint(route_strategy=RouteStrategy.ROUTESTRATEGY_SHORTEST,
                        position=position)

    def get_pose_from_apollo_waypoint(
            self, source: Source) -> Tuple[PointENU, float]:
        apollo_map = self.properties["apollo_map"]

        assert isinstance(
            apollo_map,
            ApolloHDMap), "apollo_map should be of type apollo_msgs.Map"

        map_service = MapService()
        map_service.load_map_from_proto(apollo_map)
        (point,
         heading) = map_service.get_lane_coord_and_heading(lane_id=source.id,
                                                           s=source.s)
        return (PointENU(x=point.x, y=point.y, z=0), heading)
