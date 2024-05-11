from typing import Optional, Tuple
from dataclasses import dataclass
from modules.common.proto.geometry_pb2 import PointENU
from modules.routing.proto.routing_pb2 import RoutingRequest
from openscenario_msgs import Private, ScenarioObject
from ads_scenario_transformer.transformer import Transformer
from ads_scenario_transformer.transformer.lane_waypoint_transformer import LaneWaypointTransformer, LaneWaypointTransformerConfiguration
from ads_scenario_transformer.builder.private_builder import PrivateBuilder
from ads_scenario_transformer.tools.apollo_map_parser import ApolloMapParser
from ads_scenario_transformer.tools.vector_map_parser import VectorMapParser


@dataclass
class RoutingRequestTransformerConfiguration:
    vector_map_parser: VectorMapParser
    apollo_map_parser: ApolloMapParser
    ego_scenario_object: ScenarioObject
    reference_points: Optional[Tuple[PointENU, PointENU]]


class RoutingRequestTransformer(Transformer):
    configuiration: RoutingRequestTransformerConfiguration
    Source = RoutingRequest
    Target = Private

    def __init__(self, configuration: RoutingRequestTransformerConfiguration):
        self.configuration = configuration

    def transform(self, source: Source) -> Private:
        assert len(source.waypoint
                   ) > 1, "Number of waypoints should be greater than 1"

        transformer = LaneWaypointTransformer(
            configuration=LaneWaypointTransformerConfiguration(
                vector_map_parser=self.configuration.vector_map_parser,
                apollo_map_parser=self.configuration.apollo_map_parser,
                scenario_object=self.configuration.ego_scenario_object,
                reference_points=self.configuration.reference_points))

        openscenario_waypoints = map(
            lambda lane_waypoint:
            (transformer.transform(source=lane_waypoint)), source.waypoint)

        private_builder = PrivateBuilder(
            scenario_object=self.configuration.ego_scenario_object)
        private_builder.make_routing_action_with_waypoints(
            waypoints=list(openscenario_waypoints),
            closed=False,
            name="Routing Request Transformer Generated Route")

        return private_builder.get_result()
