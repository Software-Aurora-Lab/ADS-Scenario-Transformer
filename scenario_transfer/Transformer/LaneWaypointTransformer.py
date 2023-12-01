import lanelet2
from lanelet2.core import Lanelet, LaneletMap

from apollo_msgs.basic_msgs import PointENU
from apollo_msgs.routing_msgs import LaneWaypoint
from openscenario_msgs import (LanePosition)

from ..Geometry import Geometry


class LaneWaypointTransformer:

  def __init__(self, source: LaneWaypoint) -> None:
    self.source = source
    
  def transform(self, projector, lanelet: Lanelet) -> LanePosition:

    waypoint = self.source
    if waypoint.pose:
      pose = PointENU(x=waypoint.pose.x, y=waypoint.pose.y, z=0)
      projected_point = Geometry.project_UTM_to_lanelet(
          projector=projector, pose=pose)
      return Geometry.lane_position(lanelet=lanelet,
                                    basic_point=projected_point)
