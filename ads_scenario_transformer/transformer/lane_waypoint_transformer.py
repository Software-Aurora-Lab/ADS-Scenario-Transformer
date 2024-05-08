from typing import Tuple, Optional
import math
from dataclasses import dataclass
from modules.common.proto.geometry_pb2 import PointENU
from modules.routing.proto.routing_pb2 import LaneWaypoint
from openscenario_msgs import Waypoint, RouteStrategy, ScenarioObject
from ads_scenario_transformer.transformer import Transformer
from ads_scenario_transformer.transformer.pointenu_transformer import PointENUTransformer, PointENUTransformerConfiguration, PointENUTransformerInput
from ads_scenario_transformer.tools.apollo_map_parser import ApolloMapParser
from ads_scenario_transformer.tools.vector_map_parser import VectorMapParser


@dataclass
class LaneWaypointTransformerConfiguration:
    vector_map_parser: VectorMapParser
    scenario_object: ScenarioObject
    apollo_map_parser: ApolloMapParser
    reference_points: Optional[Tuple[PointENU, PointENU]]


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
                vector_map_parser=self.configuration.vector_map_parser,
                scenario_object=self.configuration.scenario_object,
                reference_points=self.configuration.reference_points))
        position = pointenu_transformer.transform(
            PointENUTransformerInput(point=pose, heading=heading))

        return Waypoint(routeStrategy=RouteStrategy.ROUTESTRATEGY_SHORTEST,
                        position=position)

    def get_pose_from_apollo_waypoint(
            self, lane_waypoint: LaneWaypoint) -> Tuple[PointENU, float]:
        assert self.configuration.apollo_map_parser is not None

        (point, heading
         ) = self.configuration.apollo_map_parser.get_coordinate_and_heading(
             lane_id=lane_waypoint.id, s=lane_waypoint.s)
        return (PointENU(x=point.x, y=point.y, z=0), heading)
