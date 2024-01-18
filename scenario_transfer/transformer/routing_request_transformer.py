from typing import Dict

from lanelet2.core import LaneletMap
from lanelet2.projection import UtmProjector

from apollo_msgs import RoutingRequest
from openscenario_msgs import Route

from scenario_transfer.transformer import Transformer
from scenario_transfer.transformer.lane_waypoint_transformer import LaneWaypointTransformer


# properties = ["lanelet_map": lanelet2.core.LaneletMap, "projector": lanelet2.projection.UtmProjector, "apollo_map": apollo_msgs.Map, "route_name": str]
class RoutingRequestTransformer(Transformer):

    Source = RoutingRequest
    Target = Route

    def __init__(self, properties: Dict = {}):
        self.properties = properties

    def transform(self, source: Source) -> Target:

        lanelet_map = self.properties["lanelet_map"]
        projector = self.properties["projector"]

        assert isinstance(
            lanelet_map,
            LaneletMap), "lanelet should be of type lanelet2.core.Lanelet"
        assert isinstance(
            projector, UtmProjector
        ), "projector should be of type lanelet2.projection.UtmProjector"

        transformer = LaneWaypointTransformer(properties={
            "lanelet_map": lanelet_map,
            "projector": projector
        })

        if "apollo_map" in self.properties:
            transformer.properties["apollo_map"] = self.properties[
                "apollo_map"]

        openscenario_waypoints = map(
            lambda lane_waypoint:
            (transformer.transform(source=lane_waypoint)), source.waypoint)

        route_name = self.properties[
            "route_name"] if "route_name" in self.properties else ""
        route = Route(closed=False,
                      name=route_name,
                      parameter_declarations=[],
                      waypoints=openscenario_waypoints)

        return route
