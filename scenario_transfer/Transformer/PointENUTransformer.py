from typing import Type, TypeVar, List

from lanelet2.core import GPSPoint

from apollo_msgs.basic_msgs import PointENU
from openscenario_msgs import LanePosition

from .Transformable import Transformable
from ..Geometry import Geometry


# properties = [lanelet2.core.LaneletMap, lanelet2.projection.UtmProjector]
class PointENUTransformer(Transformable):
  T = PointENU
  V = GPSPoint
  X = LanePosition

  def __init__(self, properties: List = []):
    self.properties = properties

  def transform1(self, source: T) -> V:
    pose = Geometry.utm_to_WGS(pose=source)
    return pose

  def transform2(self, source: T) -> X:
    lanelet_map = self.properties[0]
    projector = self.properties[1]

    projected_point = Geometry.project_UTM_to_lanelet(projector=projector,
                                                      pose=source)
    lanelet = Geometry.find_lanelet(lanelet_map, projected_point)
    lane_position = Geometry.lane_position(lanelet=lanelet,
                                           basic_point=projected_point)
    return lane_position
