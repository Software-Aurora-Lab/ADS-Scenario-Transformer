import unittest
import lanelet2
from lanelet2.projection import MGRSProjector
from lanelet2.io import Origin
from modules.common.proto.geometry_pb2 import PointENU
from modules.routing.proto.routing_pb2 import LaneWaypoint
from openscenario_msgs import Waypoint, LanePosition
from scenario_transfer import LaneWaypointTransformer
from scenario_transfer.tools.apollo_map_service import ApolloMapService


class TestLaneWaypointTransformer(unittest.TestCase):

    def setUp(self):
        self.mgrs_projector = MGRSProjector(Origin(0, 0, 0))
        self.lanelet_map = lanelet2.io.load(
            "./samples/map/BorregasAve/lanelet2_map.osm", self.mgrs_projector)
        self.apollo_map_service = ApolloMapService()
        self.apollo_map_service.load_map_from_file(
            "./samples/map/BorregasAve/base_map.bin")

    def test_utm_type_lane_waypoint_transformer(self):
        point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)

        lane_waypoint = LaneWaypoint(pose=point)
        transformer = LaneWaypointTransformer(properties={
            "lanelet_map": self.lanelet_map,
            "projector": self.mgrs_projector
        })

        openscenario_waypoint = transformer.transform(source=lane_waypoint)
        self.assert_proto_type_equal(openscenario_waypoint, Waypoint)

        lane_position = openscenario_waypoint.position.lanePosition
        self.assert_proto_type_equal(lane_position, LanePosition)
        self.assertEqual(lane_position.laneId, "22")
        self.assertEqual(lane_position.offset, 0.1750399287494411)
        self.assertEqual(lane_position.s, 35.714714923990464)
        self.assertEqual(lane_position.orientation.h, 0)

    def test_laneId_type_lane_waypoint_transformer(self):
        lane_waypoint = LaneWaypoint(id="lane_26", s=26.2)
        transformer = LaneWaypointTransformer(
            properties={
                "lanelet_map": self.lanelet_map,
                "projector": self.mgrs_projector,
                "apollo_map_service": self.apollo_map_service
            })

        openscenario_waypoint = transformer.transform(source=lane_waypoint)
        self.assert_proto_type_equal(openscenario_waypoint, Waypoint)
        lane_position = openscenario_waypoint.position.lanePosition
        
        self.assert_proto_type_equal(lane_position, LanePosition)
        self.assertEqual(lane_position.laneId, "149")
        self.assertEqual(lane_position.offset, 1.4604610803960605)
        self.assertEqual(lane_position.s, 26.739416492972932)
        self.assertEqual(lane_position.orientation.h, -1.9883158777364047)

    def assert_proto_type_equal(self, reflection_type, pb2_type):
        self.assertEqual(str(reflection_type.__class__), str(pb2_type))

if __name__ == '__main__':
    unittest.main()
