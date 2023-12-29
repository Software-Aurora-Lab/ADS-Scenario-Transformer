import unittest
import yaml

import lanelet2
from lanelet2.projection import UtmProjector
from lanelet2.io import Origin
from pytest import fail

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
        transformer = PointENUTransformer(properties=[worldType])
        position = transformer.transform(source=point)

        self.assertIsNotNone(position.world_position,
                             "The gpspoint should not be None.")
        yaml_data = FormatTransformer.transform_proto_pyobject_to_yaml(
            position)

        python_object = yaml.safe_load(yaml_data)

        print("pr", type(python_object), python_object)
        # # Save the YAML to a file or print it
        with open('output.yaml', 'w') as file:
            file.write(yaml_data)

        self.assertFalse(false)

    def test_transform_lane_position(self):
        point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
        laneType = PointENUTransformer.SupportedPosition.Lane
        transformer = PointENUTransformer(
            properties=[laneType, self.map, self.utm_projector])
        position = transformer.transform(source=point)
        self.assertIsNotNone(position.lane_position,
                             "The lane_position should not be None.")

        yaml_data = FormatTransformer.transform_proto_pyobject_to_yaml(
            position)

        with open('output2.yaml', 'w') as file:
            file.write(yaml_data)

        # self.assertFalse(false)
