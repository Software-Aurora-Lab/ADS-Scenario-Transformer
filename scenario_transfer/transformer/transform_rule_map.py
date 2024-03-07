from dataclasses import dataclass
from modules.common.proto.geometry_pb2 import PointENU
from modules.routing.proto.routing_pb2 import RoutingRequest, LaneWaypoint
from openscenario_msgs import Position, Waypoint, Route, Private


@dataclass
class TransformRuleContainer:
    rules = {
        type(PointENU): [type(Position)],
        type(LaneWaypoint): [type(Waypoint)],
        type(RoutingRequest): type(Private)
    }
