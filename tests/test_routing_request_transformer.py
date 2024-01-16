import unittest
import json

import lanelet2
from lanelet2.projection import UtmProjector
from lanelet2.io import Origin

from apollo_msgs import Header, RoutingRequest
from openscenario_msgs import Route, LanePosition

from scenario_transfer import RoutingRequestTransformer
from scenario_transfer.apollo_map_io_handler import ApolloMapIOHandler as MapIOHandler
from scenario_transfer import FormatTransformer


class TestTransformer(unittest.TestCase):

    def setUp(self):
        origin = Origin(37.04622247590861, -123.00000000000001, 0)
        self.utm_projector = UtmProjector(origin)
        self.lanelet_map = lanelet2.io.load(
            "./samples/map/BorregasAve/lanelet2_map.osm", self.utm_projector)
        map_io_handler = MapIOHandler()
        self.apollo_map = map_io_handler.load_map(
            "./samples/map/BorregasAve/base_map.bin")

    def test_routing_request(self):
        routing_request_transformer = RoutingRequestTransformer(
            properties={
                "lanelet_map": self.lanelet_map,
                "projector": self.utm_projector,
                "apollo_map": self.apollo_map,
                "route_name": "test_route"
            })
        with open(
                "./samples/apollo_borregas/00000009.00000_routing_request.json",
                'r') as file:
            json_data = file.read()

        raw_dict = json.loads(json_data)
        routing_request_dict = raw_dict["ROUTING_REQUEST"][0]
        routing_request = RoutingRequest(**routing_request_dict)

        openscenario_route = routing_request_transformer.transform(
            routing_request)

        print(openscenario_route)
        self.assertIsInstance(
            openscenario_route, Route,
            "The openscenario_route should be of type Route")

        waypoint1 = openscenario_route.waypoints[0]
        lane_position1 = waypoint1.position.lane_position
        self.assertIsInstance(
            lane_position1, LanePosition,
            "The waypoint.lane_position should be of type LanePosition.")

        self.assertEqual(lane_position1.lane_id, "22")
        self.assertEqual(lane_position1.offset, 0.1750399287494411)
        self.assertEqual(lane_position1.s, 35.714714923990464)
        self.assertEqual(lane_position1.orientation.h, 2.883901414579166)

        waypoint2 = openscenario_route.waypoints[-1]
        lane_position2 = waypoint2.position.lane_position

        self.assertEqual(lane_position2.lane_id, "149")
        self.assertEqual(lane_position2.offset, 1.4604610803960605)
        self.assertEqual(lane_position2.s, 26.739416492972932)
        self.assertEqual(lane_position2.orientation.h, -1.9883158777364047)


if __name__ == '__main__':
    unittest.main()
