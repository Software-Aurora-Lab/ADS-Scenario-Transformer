import unittest
import lanelet2
from lanelet2.projection import MGRSProjector
from lanelet2.io import Origin
from modules.common.proto.geometry_pb2 import PointENU
from scenario_transfer import PointENUTransformer


class TestPointENUTransformer(unittest.TestCase):

    def setUp(self):
        origin = Origin(37.04622247590861, -123.00000000000001, 0)
        self.mgrs_Projector = MGRSProjector(origin)
        self.map = lanelet2.io.load(
            "./samples/map/BorregasAve/lanelet2_map.osm", self.mgrs_Projector)

    def test_transform_world_position(self):
        point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
        worldType = PointENUTransformer.SupportedPosition.World
        transformer = PointENUTransformer(
            properties={"supported_position": worldType})
        position = transformer.transform(source=(point, 0.0))

        self.assertIsNotNone(position.worldPosition,
                             "The gpspoint should not be None.")
        self.assertEqual(position.worldPosition.x, 37.416880423172465)
        self.assertEqual(position.worldPosition.y, -122.01593194093681)
        self.assertEqual(position.worldPosition.z, 0.0)

    def test_transform_lane_position(self):
        point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
        laneType = PointENUTransformer.SupportedPosition.Lane
        transformer = PointENUTransformer(
            properties={
                "supported_position": laneType,
                "lanelet_map": self.map,
                "projector": self.mgrs_Projector
            })
        position = transformer.transform(source=(point, 0.0))

        self.assertIsNotNone(position.lanePosition,
                             "The lane_position should not be None.")

        self.assertEqual(position.lanePosition.laneId, "22")
        self.assertEqual(position.lanePosition.s, 35.71471492399046)
        self.assertEqual(position.lanePosition.offset, 0.1750399287494411)


if __name__ == '__main__':
    unittest.main()
