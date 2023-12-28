from dataclasses import dataclass

from apollo_msgs.basic_msgs import PointENU
from apollo_msgs.routing_msgs import LaneWaypoint
from openscenario_msgs import Position, Waypoint


@dataclass
class TransformRuleContainer:
  rules = {
      type(PointENU): [type(Position)],
      type(LaneWaypoint): [type(Waypoint)]
  }
