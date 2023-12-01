from dataclasses import dataclass

from apollo_msgs.basic_msgs import PointENU
from apollo_msgs.routing_msgs import LaneWaypoint
from openscenario_msgs import LanePosition

from lanelet2.core import GPSPoint


@dataclass
class TransformRuleContainer:
  rules = {
      type(PointENU): [type(GPSPoint), type(LanePosition)],
      type(LaneWaypoint): [type(LanePosition)]
  }
