import unittest
import pytest

from apollo_msgs import PointENU
from openscenario_msgs.position_pb2 import LanePosition
from openscenario_msgs.route_pb2 import Waypoint
from openscenario_msgs import EntityRef
from openscenario_msgs import Vehicle

class TestProtocolBuffers(unittest.TestCase):

    def test_apollo_protocol_import(self):
        point1 = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
        point2 = PointENU(x=587044.4300003723, y=4141550.060588833, z=0)

        self.assertEqual(point1.x, 587079.3045861976)
        self.assertEqual(point1.y, 4141574.299574421)
        self.assertEqual(point2.x, 587044.4300003723)
        self.assertEqual(point2.y, 4141550.060588833)
    
    def test_openscenario_protocol_import(self):
        position1 = LanePosition(lane_id="154", s=10.9835, offset=-0.5042)
        position2 = LanePosition(lane_id="108", s=35.266, offset=-1.1844)
        
        self.assertEqual(position1.lane_id, "154")
        self.assertEqual(position1.s, 10.9835)
        self.assertEqual(position1.offset, -0.5042)
        self.assertEqual(position2.lane_id, "108")
        self.assertEqual(position2.s, 35.266)
        self.assertEqual(position2.offset, -1.1844)

if __name__ == '__main__':
    unittest.main()
