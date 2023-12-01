from dataclasses import dataclass

from apollo_msgs import PointENU
from openscenario_msgs import LanePosition
from ..LaneWayPoint import LaneWaypoint
from lanelet2.core import GPSPoint

@dataclass
class TransformRuleContainer:
    rules = {
        type(PointENU): [type(GPSPoint), type(LanePosition)],
        type(LaneWaypoint): [type(LanePosition)]
    }