from dataclasses import dataclass

from apollo_msgs.basic_msgs import PointENU
from apollo_msgs.routing_msgs import LaneWaypoint, RoutingRequest
from openscenario_msgs import Position, Waypoint, Route, Private


@dataclass
class TransformRuleContainer:
    rules = {
        type(PointENU): [type(Position)],
        type(LaneWaypoint): [type(Waypoint)],
        type(RoutingRequest): type(Private)
    }
