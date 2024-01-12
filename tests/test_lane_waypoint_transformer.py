import unittest

import lanelet2
from lanelet2.projection import UtmProjector
from lanelet2.io import Origin

from apollo_msgs.basic_msgs import PointENU
from apollo_msgs.routing_msgs import LaneWaypoint
from openscenario_msgs import Waypoint, LanePosition

from scenario_transfer import Geometry, LaneWaypointTransformer
from scenario_transfer.apollo_map_io_handler import ApolloMapIOHandler as MapIOHandler


class TestTransformer(unittest.TestCase):

    def setUp(self):
        origin = Origin(37.04622247590861, -123.00000000000001, 0)
        self.utm_projector = UtmProjector(origin)
        self.lanelet_map = lanelet2.io.load(
            "./samples/map/BorregasAve/lanelet2_map.osm", self.utm_projector)
        map_io_handler = MapIOHandler()
        self.apollo_map = map_io_handler.load_map("./samples/map/BorregasAve/base_map.bin")
        
    def test_utm_type_lane_waypoint_transformer(self):
        point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
        
        lane_waypoint = LaneWaypoint(pose=point)
        transformer = LaneWaypointTransformer(properties={"lanelet_map": self.lanelet_map, "projector": self.utm_projector})
        
        openscenario_waypoint = transformer.transform(source=lane_waypoint)
        self.assertIsInstance(openscenario_waypoint, Waypoint, "The waypoint should be of type Waypoint.")

        lane_position = openscenario_waypoint.position.lane_position
        self.assertIsInstance(lane_position, LanePosition, "The waypoint.lane_position should be of type LanePosition.")

        self.assertEqual(lane_position.lane_id, "22")
        self.assertEqual(lane_position.offset, 0.1750399287494411)
        self.assertEqual(lane_position.s, 35.714714923990464)
        self.assertEqual(lane_position.orientation.h, 0)
        
    def test_lane_id_type_lane_waypoint_transformer(self):
        lane_waypoint = LaneWaypoint(id="lane_26", s=26.2)
        transformer = LaneWaypointTransformer(properties={"lanelet_map": self.lanelet_map, "projector": self.utm_projector, "apollo_map": self.apollo_map})

        openscenario_waypoint = transformer.transform(source=lane_waypoint)
        self.assertIsInstance(openscenario_waypoint, Waypoint, "The waypoint should be of type Waypoint.")

        lane_position = openscenario_waypoint.position.lane_position
        self.assertIsInstance(lane_position, LanePosition, "The waypoint.lane_position should be of type LanePosition.")

        self.assertEqual(lane_position.lane_id, "149")
        self.assertEqual(lane_position.offset, 1.4604610803960605)
        self.assertEqual(lane_position.s, 26.739416492972932)
        self.assertEqual(lane_position.orientation.h, -1.9883158777364047)
        

if __name__ == '__main__':
    unittest.main()
