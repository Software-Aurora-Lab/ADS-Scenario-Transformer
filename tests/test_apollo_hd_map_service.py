import unittest

from apollo_msgs import Map
from pkgs.scenorita.map_service import MapService

from scenario_transfer.apollo_map_io_handler import ApolloMapIOHandler as MapIOHandler

class TestApolloHDMapService(unittest.TestCase):

    def setUp(self):
        self.binary_map_path = "./samples/map/BorregasAve/base_map.bin"
        map_io_handler = MapIOHandler()
        self.map = map_io_handler.load_map(self.binary_map_path)
        
    def test_apollo_map_lane_to_utm(self):
        map_service = MapService()
        map_service.load_map_from_proto(self.map)
        (point1, heading1) = map_service.get_lane_coord_and_heading(lane_id="lane_26", s=26.2)
        self.assertEqual(point1.x, 586969.5290636807)
        self.assertEqual(point1.y, 4141286.5458221673)
        self.assertEqual(heading1, -1.9883158777364047)

        (point2, heading2) = map_service.get_lane_coord_and_heading(lane_id="lane_30", s=0.0)
        self.assertEqual(point2.x, 587040.39095115662)
        self.assertEqual(point2.y, 4141553.0670471191)
        self.assertEqual(heading2, -1.807509475733681)
        

if __name__ == '__main__':
    unittest.main()
