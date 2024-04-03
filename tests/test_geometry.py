import unittest
import lanelet2
from lanelet2.projection import MGRSProjector
from lanelet2.core import BasicPoint3d
from lanelet2.io import Origin
from modules.common.proto.geometry_pb2 import PointENU
from openscenario_msgs import LanePosition
from scenario_transfer.tools.geometry import Geometry


class TestGeometry(unittest.TestCase):

    def setUp(self):
        origin = Origin(37.04622247590861, -123.00000000000001, 0)
        self.mgrs_Projector = MGRSProjector(origin)
        self.map = lanelet2.io.load(
            "./samples/map/BorregasAve/lanelet2_map.osm", self.mgrs_Projector)

    def test_load_map(self):
        self.assertIsNotNone(self.map, "Map should not be None")

    def prop(self, obj):
        return str(type(obj)) + ' ' + str(
            list(filter(lambda name: not name.startswith('__'), dir(obj))))

    def test_projection(self):
        poses = [
            PointENU(x=587079.3045861976, y=4141574.299574421, z=0),
            PointENU(x=587044.4300003723, y=4141550.060588833, z=0)
        ]

        expectations = [
            BasicPoint3d(87079.3, 41574.3, 0),
            BasicPoint3d(87044.4, 41550.1, 0)
        ]

        for pose, expectation in zip(poses, expectations):
            projected = Geometry.project_UTM_to_lanelet(
                projector=self.mgrs_Projector, pose=pose)
            self.assertAlmostEqual(
                abs(projected.x - expectation.x),
                second=1.0,
                msg="projected point.x is not equal to the expectation",
                delta=1.0)
            self.assertAlmostEqual(
                abs(projected.y - expectation.y),
                second=1.0,
                msg="projected point.y is not equal to the expectation",
                delta=1.0)

    def test_geometry(self):
        basic_points = [
            BasicPoint3d(86973.4293, 41269.817, -5.6757),
            BasicPoint3d(86993.2289, 41343.5182, -4.5032),
            BasicPoint3d(87014.2461, 41427.1901, -3.2535),
            BasicPoint3d(87079.3, 41574.3, 0)
        ]

        expectations = [
            LanePosition(laneId="154", s=10.9835, offset=-0.5042),
            LanePosition(laneId="108", s=35.266, offset=-1.1844),
            LanePosition(laneId="108", s=121.5308, offset=-0.134),
            LanePosition(laneId="22", s=35.7761, offset=-0.2818)
        ]

        for idx, (basic_point,
                  expectation) in enumerate(zip(basic_points, expectations)):
            Geometry.find_lanelet(self.map, basic_point)
            lanelet = Geometry.find_lanelet(map=self.map,
                                            basic_point=basic_point)
            self.assertIsNotNone(lanelet, "lanelet should not be None")

            target_lane_position = Geometry.lane_position(
                lanelet=lanelet, basic_point=basic_point)

            self.assertEqual(target_lane_position.laneId, expectation.laneId,
                             "laneId should be the same")
            self.assertAlmostEqual(
                abs(target_lane_position.s - expectation.s),
                second=1.0,
                msg="s attribute should be almost equal to expectation",
                delta=1.0)
            self.assertAlmostEqual(
                abs(target_lane_position.offset - expectation.offset),
                second=1.0,
                msg="t attribute should be almost equal to expectation",
                delta=2.0)


if __name__ == '__main__':
    unittest.main()
