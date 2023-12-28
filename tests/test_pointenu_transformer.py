import unittest

import pytest
import lanelet2
from lanelet2.projection import UtmProjector
from lanelet2.io import Origin

from apollo_msgs.basic_msgs import PointENU
from scenario_transfer import PointENUTransformer, LaneWaypointTransformer


class TestTransformer(unittest.TestCase):

    def setUp(self):
        origin = Origin(37.04622247590861, -123.00000000000001, 0)
        self.utm_projector = UtmProjector(origin)
        self.map = lanelet2.io.load(
            "./samples/map/BorregasAve/lanelet2_map.osm", self.utm_projector)

    def test_transform_world_position(self):
        point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
        worldType = PointENUTransformer.SupportedPosition.World
        transformer = PointENUTransformer(properties=[worldType])
        position = transformer.transform(source=point)
        self.assertIsNotNone(position.world_position,
                             "The gpspoint should not be None.")

    def test_transform_lane_position(self):
        point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
        laneType = PointENUTransformer.SupportedPosition.Lane
        transformer = PointENUTransformer(
            properties=[laneType, self.map, self.utm_projector])
        position = transformer.transform(source=point)
        self.assertIsNotNone(position.lane_position,
                             "The lane_position should not be None.")


if __name__ == '__main__':
    unittest.main()
