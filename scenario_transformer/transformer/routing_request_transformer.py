from typing import Dict, Optional
from dataclasses import dataclass
from lanelet2.core import LaneletMap
from lanelet2.projection import MGRSProjector
from modules.routing.proto.routing_pb2 import RoutingRequest
from openscenario_msgs import Route, Private, ScenarioObject
from scenario_transformer.transformer import Transformer
from scenario_transformer.transformer.lane_waypoint_transformer import LaneWaypointTransformer, LaneWaypointTransformerConfiguration
from scenario_transformer.builder.private_builder import PrivateBuilder
from scenario_transformer.tools.apollo_map_parser import ApolloMapParser

@dataclass
class RoutingRequestTransformerConfiguration:
    lanelet_map: LaneletMap
    projector: MGRSProjector
    ego_scenario_object: ScenarioObject
    apollo_map_parser: Optional[ApolloMapParser] = None
    
    
class RoutingRequestTransformer(Transformer):
    configuiration: RoutingRequestTransformerConfiguration
    Source = RoutingRequest
    Target = Private

    def __init__(self, configuration: RoutingRequestTransformerConfiguration):
        self.configuration = configuration

    def transform(self, source: Source) -> Target:

        transformer = LaneWaypointTransformer(configuration=LaneWaypointTransformerConfiguration(
            lanelet_map=self.configuration.lanelet_map, 
            projector=self.configuration.projector,
            apollo_map_parser = self.configuration.apollo_map_parser)
        )
 
        openscenario_waypoints = map(
            lambda lane_waypoint:
            (transformer.transform(source=lane_waypoint)), source.waypoint)

        private_builder = PrivateBuilder(scenario_object=self.configuration.ego_scenario_object)
        private_builder.make_routing_action_with_teleport_action(
            waypoints=list(openscenario_waypoints),
            closed=False, 
            name="Routing Request Transformer Generated Route")
        
        private = private_builder.get_result()
        return private
