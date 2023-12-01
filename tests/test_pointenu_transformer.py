import unittest
from pyproj import Geod

import pytest
import lanelet2
from lanelet2.projection import UtmProjector
from lanelet2.io import Origin

from apollo_msgs.basic_msgs import PointENU
from apollo_msgs.routing_msgs import LaneWaypoint

from openscenario_msgs import LanePosition

from scenario_transfer import Geometry, PointENUTransformer, LaneWaypointTransformer


class TestTransformer(unittest.TestCase):

  def setUp(self):
    origin = Origin(37.04622247590861, -123.00000000000001, 0)
    self.utm_projector = UtmProjector(origin)
    self.map = lanelet2.io.load("./samples/map/BorregasAve/lanelet2_map.osm",
                                self.utm_projector)

  def test_transform1(self):
    point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
    transformer = PointENUTransformer()
    gpspoint = transformer.transform1(source=point)
    self.assertIsNotNone(gpspoint, "The gpspoint should not be None.")

  def test_transform2(self):
    point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
    transformer = PointENUTransformer(
        properties=[self.map, self.utm_projector])
    lane_position = transformer.transform2(source=point)
    self.assertIsNotNone(lane_position,
                         "The lane_position should not be None.")

  def test_LaneWaypoint_Transformer(self):
    point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
    waypoint = LaneWaypoint(pose=point)
    projected_point = Geometry.project_UTM_to_lanelet(self.utm_projector,
                                                      point)
    lanelet = Geometry.find_lanelet(map=self.map, basic_point=projected_point)

    if not lanelet:
      assert False, "This assertion will always fail"

    transformer = LaneWaypointTransformer(source=waypoint)
    laneposition = transformer.transform(projector=self.utm_projector,
                                         lanelet=lanelet)
    self.assertIsNotNone(laneposition, "The laneposition should not be None.")


if __name__ == '__main__':
  unittest.main()
