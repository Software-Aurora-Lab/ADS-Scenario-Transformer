from typing import Dict
from lanelet2.core import LaneletMap
from lanelet2.projection import MGRSProjector
from modules.routing.proto.routing_pb2 import RoutingRequest
from openscenario_msgs import Route, Private, ScenarioObject
from scenario_transfer.transformer import Transformer
from scenario_transfer.transformer.lane_waypoint_transformer import LaneWaypointTransformer
from scenario_transfer.builder.private_builder import PrivateBuilder


class RoutingRequestTransformer(Transformer):
    """
    = properties = [
        "lanelet_map": lanelet2.core.LaneletMap, 
        "projector": lanelet2.projection.MGRSProjector, 
        "apollo_map_service": ApolloMapService, 
        "route_name": str,
        "ego_scenario_object": ScenarioObject
    ]
    """
    Source = RoutingRequest
    Target = Private

    def __init__(self, properties: Dict = {}):
        self.properties = properties

    def transform(self, source: Source) -> Target:

        lanelet_map = self.properties["lanelet_map"]
        projector = self.properties["projector"]
        ego = self.properties["ego_scenario_object"]

        assert isinstance(
            lanelet_map,
            LaneletMap), "lanelet should be of type lanelet2.core.Lanelet"
        assert isinstance(
            projector, MGRSProjector
        ), "projector should be of type lanelet2.projection.MGRSProjector"

        assert str(ego.__class__) == str(ScenarioObject), "ego should be of type ScenarioObject"

        transformer = LaneWaypointTransformer(properties={
            "lanelet_map": lanelet_map,
            "projector": projector
        })

        if "apollo_map_service" in self.properties:
            transformer.properties["apollo_map_service"] = self.properties[
                "apollo_map_service"]

        openscenario_waypoints = map(
            lambda lane_waypoint:
            (transformer.transform(source=lane_waypoint)), source.waypoint)

        private_builder = PrivateBuilder(scenario_object=ego)
        private_builder.make_routing_action_with_teleport_action(
            waypoints=list(openscenario_waypoints),
            closed=False, 
            name="Routing Request Transformer Generated Route")
        
        private = private_builder.get_result()
        return private
