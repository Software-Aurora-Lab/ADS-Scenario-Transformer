import unittest
import json

import lanelet2
from lanelet2.projection import MGRSProjector
from lanelet2.io import Origin
from apollo_msgs import RoutingRequest
from openscenario_msgs import Private, TeleportAction, RoutingAction, AssignRouteAction, Route, LanePosition
from scenario_transfer import RoutingRequestTransformer
from scenario_transfer.tools.apollo_map_service import ApolloMapService
from scenario_transfer.builder import EntitiesBuilder
from scenario_transfer.builder.entities_builder import EntityType


class TestRoutingRequestTransformer(unittest.TestCase):

    def setUp(self):
        origin = Origin(37.04622247590861, -123.00000000000001, 0)
        self.mgrs_Projector = MGRSProjector(origin)
        self.lanelet_map = lanelet2.io.load(
            "./samples/map/BorregasAve/lanelet2_map.osm", self.mgrs_Projector)
        self.apollo_map_service = ApolloMapService()
        self.apollo_map_service.load_map_from_file(
            "./samples/map/BorregasAve/base_map.bin")

        builder = EntitiesBuilder(entities=[EntityType.EGO])
        self.ego = builder.get_result().scenarioObjects[0]

    def test_routing_request(self):
        routing_request_transformer = RoutingRequestTransformer(
            properties={
                "lanelet_map": self.lanelet_map,
                "projector": self.mgrs_Projector,
                "apollo_map_service": self.apollo_map_service,
                "route_name": "test_route",
                "ego_scenario_object": self.ego
            })
        with open(
                "./samples/apollo_borregas/00000009.00000_routing_request.json",
                'r') as file:
            json_data = file.read()

        raw_dict = json.loads(json_data)
        routing_request_dict = raw_dict["ROUTING_REQUEST"][0]
        routing_request = RoutingRequest(**routing_request_dict)

        openscenario_private = routing_request_transformer.transform(
            routing_request)

        self.assertIsInstance(openscenario_private, Private,
                              "The private should be of type Private")

        self.assertEqual(openscenario_private.entityRef, "ego")

        teleport_action = openscenario_private.privateActions[0].teleportAction
        routing_action = openscenario_private.privateActions[1].routingAction
        self.assertIsInstance(teleport_action, TeleportAction)
        self.assertIsInstance(routing_action, RoutingAction)

        start_lane_position = teleport_action.position.lanePosition
        self.assertEqual(start_lane_position.lane_id, "22")
        self.assertEqual(start_lane_position.offset, 0.1750399287494411)
        self.assertEqual(start_lane_position.s, 35.714714923990464)
        self.assertEqual(start_lane_position.orientation.h, 2.883901414579166)

        self.assertIsInstance(routing_action.assignRouteAction,
                              AssignRouteAction)

        end_waypoint = routing_action.assignRouteAction.route.waypoints[-1]
        end_lane_position = end_waypoint.position.lanePosition

        self.assertEqual(end_lane_position.lane_id, "149")
        self.assertEqual(end_lane_position.offset, 1.4604610803960605)
        self.assertEqual(end_lane_position.s, 26.739416492972932)
        self.assertEqual(end_lane_position.orientation.h, -1.9883158777364047)


if __name__ == '__main__':
    unittest.main()
