import unittest

import lanelet2
from lanelet2.projection import UtmProjector
from lanelet2.io import Origin

from apollo_msgs.basic_msgs import PointENU
from apollo_msgs.routing_msgs import LaneWaypoint
from openscenario_msgs import Waypoint, LanePosition

from scenario_transfer import Geometry, LaneWaypointTransformer


class TestTransformer(unittest.TestCase):

    def setUp(self):
        origin = Origin(37.04622247590861, -123.00000000000001, 0)
        self.utm_projector = UtmProjector(origin)
        self.map = lanelet2.io.load(
            "./samples/map/BorregasAve/lanelet2_map.osm", self.utm_projector)

    def test_lane_waypoint_Transformer(self):
        point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
        lane_waypoint = LaneWaypoint(pose=point)
        projected_point = Geometry.project_UTM_to_lanelet(
            self.utm_projector, point)
        lanelet = Geometry.find_lanelet(map=self.map,
                                        basic_point=projected_point)

        if not lanelet:
            assert False, "lanelet should not be empty"

        transformer = LaneWaypointTransformer(
            properties=[lanelet, self.utm_projector])
        waypoint = transformer.transform(source=lane_waypoint)
        self.assertIsInstance(waypoint, Waypoint,
                              "The waypoint should be of type Waypoint.")
        self.assertIsInstance(
            waypoint.position.lane_position, LanePosition,
            "The waypoint.lane_position should be of type LanePosition.")


if __name__ == '__main__':
    unittest.main()
