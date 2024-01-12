import unittest
import yaml

import lanelet2
from lanelet2.projection import UtmProjector
from lanelet2.io import Origin

from apollo_msgs.basic_msgs import PointENU
from scenario_transfer import PointENUTransformer, FormatTransformer


class TestTransformer(unittest.TestCase):

    def setUp(self):
        origin = Origin(37.04622247590861, -123.00000000000001, 0)
        self.utm_projector = UtmProjector(origin)
        self.map = lanelet2.io.load(
            "./samples/map/BorregasAve/lanelet2_map.osm", self.utm_projector)

    def test_transform_world_position(self):
        point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
        worldType = PointENUTransformer.SupportedPosition.World
        transformer = PointENUTransformer(properties={"supported_position": worldType})
        position = transformer.transform(source=point)
        
        self.assertIsNotNone(position.world_position,
                             "The world_position should not be None.")
        yaml_data = FormatTransformer.transform_proto_pyobject_to_yaml(
            position)

        py_dict = yaml.safe_load(yaml_data)
        world_position_dict = py_dict['Position']['WorldPosition']
        self.assertEqual(world_position_dict['x'], 37.416880423172465)
        self.assertEqual(world_position_dict['y'], -122.01593194093681)

    def test_transform_lane_position(self):
        point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
        laneType = PointENUTransformer.SupportedPosition.Lane
        transformer = PointENUTransformer(
            properties={"supported_position": laneType, "lanelet_map": self.map, "projector": self.utm_projector})
        position = transformer.transform(source=point)
        self.assertIsNotNone(position.lane_position,
                             "The lane_position should not be None.")
        
        yaml_data = FormatTransformer.transform_proto_pyobject_to_yaml(
            position)
        py_dict = yaml.safe_load(yaml_data)

        lane_position_dict = py_dict['Position']['LanePosition']
        self.assertEqual(lane_position_dict['roadId'], '')
        self.assertEqual(lane_position_dict['laneId'], '22')
        self.assertEqual(lane_position_dict['offset'], 0.1750399287494411)
        self.assertEqual(lane_position_dict['s'], 35.71471492399046)
        self.assertEqual(lane_position_dict['orientation']['type'], 'relative')
