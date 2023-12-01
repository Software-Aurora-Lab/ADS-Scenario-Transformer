from dataclasses import dataclass
from typing import Optional
from apollo_msgs import PointENU 

# TODO: This class is temporary dataclass. It should be replaced to LaneWayPoint in apollo_msgs
@dataclass
class LaneWaypoint:
    id: Optional[str] = None
    s: Optional[float] = None
    pose: Optional[PointENU] = None
    heading: Optional[float] = None