from typing import Dict, Tuple, Optional, Set
import math
from dataclasses import dataclass
from lanelet2.core import LaneletMap
from lanelet2.projection import MGRSProjector
from modules.common.proto.geometry_pb2 import PointENU
from modules.routing.proto.routing_pb2 import LaneWaypoint
from openscenario_msgs import (Waypoint, RouteStrategy)
from ads_scenario_transformer.transformer import Transformer
from ads_scenario_transformer.transformer.pointenu_transformer import PointENUTransformer, PointENUTransformerConfiguration
from ads_scenario_transformer.tools.apollo_map_parser import ApolloMapParser


@dataclass
class LaneWaypointTransformerConfiguration:
    lanelet_map: LaneletMap
    projector: MGRSProjector
    lanelet_subtypes: Set[str]
    apollo_map_parser: Optional[ApolloMapParser] = None


class LaneWaypointTransformer(Transformer):
    configuration: LaneWaypointTransformerConfiguration
    Source = LaneWaypoint
    Target = Waypoint

    def __init__(self, configuration: LaneWaypointTransformerConfiguration):
        self.configuration = configuration

    def transform(self, source: Source) -> Target:
        pose = source.pose
        heading = source.heading if source.heading else 0.0

        if math.isnan(
                pose.x
        ):  # if pose.x and pose.y are nan, then it will check laneId and s
            (pose, heading) = self.get_pose_from_apollo_waypoint(source)

        pointenu_transformer = PointENUTransformer(
            configuration=PointENUTransformerConfiguration(
                supported_position=PointENUTransformer.SupportedPosition.Lane,
                lanelet_map=self.configuration.lanelet_map,
                projector=self.configuration.projector,
                lanelet_subtypes=self.configuration.lanelet_subtypes))
        position = pointenu_transformer.transform((pose, heading))

        return Waypoint(routeStrategy=RouteStrategy.ROUTESTRATEGY_SHORTEST,
                        position=position)

    def get_pose_from_apollo_waypoint(
            self, source: Source) -> Tuple[PointENU, float]:
        assert self.configuration.apollo_map_parser is not None

        (point, heading
         ) = self.configuration.apollo_map_parser.get_coordinate_and_heading(
             lane_id=source.id, s=source.s)
        return (PointENU(x=point.x, y=point.y, z=0), heading)
