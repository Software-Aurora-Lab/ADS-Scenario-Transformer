import unittest
import yaml
import json

from openscenario_msgs import Route, LanePosition

from scenario_transfer.openscenario import OpenScenarioEncoder, OpenScenarioDecoder


class TestOpenScenarioCoder(unittest.TestCase):

    def setUp(self):
        with open("./samples/test_data/openscenario_route.json", 'r') as file:
            self.json_data = file.read()

    def test_openscenario_encode_decode(self):
        raw_dict = json.loads(self.json_data)
        openscenario_route = Route(**raw_dict)
        encoded_data = OpenScenarioEncoder.encode_proto_pyobject_to_yaml(
            openscenario_route)

        decoded_data = yaml.safe_load(encoded_data)

        self.assertIsNotNone(decoded_data["Route"])
        self.assertIsNotNone(decoded_data["Route"]["Waypoint"])
        self.assertIsInstance(decoded_data["Route"]["Waypoint"], list)
        self.assertIsNotNone(decoded_data["Route"]["Waypoint"][0]["Position"])
        self.assertIsNotNone(
            decoded_data["Route"]["Waypoint"][0]["Position"]["LanePosition"])

        openscenario_route = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=decoded_data, type_=Route, exclude_top_level_key=True)

        self.assertIsInstance(openscenario_route, Route)

        start_waypoint = openscenario_route.waypoints[0]
        start_lane_position = start_waypoint.position.lane_position
        self.assertIsInstance(
            start_lane_position, LanePosition,
            "The waypoint.lane_position should be of type LanePosition.")

        self.assertEqual(start_lane_position.lane_id, "22")
        self.assertEqual(start_lane_position.offset, 0.1750399287494411)
        self.assertEqual(start_lane_position.s, 35.714714923990464)
        self.assertEqual(start_lane_position.orientation.h, 2.883901414579166)

        end_waypoint = openscenario_route.waypoints[-1]
        end_lane_position = end_waypoint.position.lane_position

        self.assertEqual(end_lane_position.lane_id, "149")
        self.assertEqual(end_lane_position.offset, 1.4604610803960605)
        self.assertEqual(end_lane_position.s, 26.739416492972932)
        self.assertEqual(end_lane_position.orientation.h, -1.9883158777364047)
