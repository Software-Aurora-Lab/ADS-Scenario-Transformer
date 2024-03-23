import unittest
import lanelet2
from lanelet2.projection import MGRSProjector
from lanelet2.io import Origin
from openscenario_msgs import Private, TeleportAction, RoutingAction, AssignRouteAction
from scenario_transfer.transformer import RoutingRequestTransformer
from scenario_transfer.tools.apollo_map_service import ApolloMapService
from scenario_transfer.builder import EntitiesBuilder
from scenario_transfer.builder.entities_builder import EntityType
from scenario_transfer.openscenario import OpenScenarioEncoder
from scenario_transfer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel


class TestRoutingRequestTransformer(unittest.TestCase):

    def setUp(self):
        origin = Origin(0, 0, 0)
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

        routing_requests = CyberRecordReader.read_channel(
            source_path="./samples/apollo_borregas/00000009.00000",
            channel=CyberRecordChannel.ROUTING_REQUEST)

        routing_request = routing_requests[0]
        openscenario_private = routing_request_transformer.transform(
            routing_request)

        self.assert_proto_type_equal(openscenario_private, Private)
        self.assertEqual(openscenario_private.entityRef, "ego")

        teleport_action = openscenario_private.privateActions[0].teleportAction
        routing_action = openscenario_private.privateActions[1].routingAction
        self.assert_proto_type_equal(teleport_action, TeleportAction)
        self.assert_proto_type_equal(routing_action, RoutingAction)

        start_lane_position = teleport_action.position.lanePosition
        self.assertEqual(start_lane_position.laneId, "22")
        self.assertEqual(start_lane_position.offset, 0.1750399287494411)
        self.assertEqual(start_lane_position.s, 35.714714923990464)
        self.assertEqual(start_lane_position.orientation.h, 2.883901414579166)

        self.assert_proto_type_equal(routing_action.assignRouteAction,
                                     AssignRouteAction)

        end_waypoint = routing_action.assignRouteAction.route.waypoints[-1]
        end_lane_position = end_waypoint.position.lanePosition

        self.assertEqual(end_lane_position.laneId, "149")
        self.assertEqual(end_lane_position.offset, 1.4604610803960605)
        self.assertEqual(end_lane_position.s, 26.739416492972932)
        self.assertEqual(end_lane_position.orientation.h, -1.9883158777364047)

    def test_routing_request_from_response(self):
        routing_request_transformer = RoutingRequestTransformer(
            properties={
                "lanelet_map": self.lanelet_map,
                "projector": self.mgrs_Projector,
                "apollo_map_service": self.apollo_map_service,
                "route_name": "test_route",
                "ego_scenario_object": self.ego
            })
        routing_responses = CyberRecordReader.read_channel(
            source_path="./samples/apollo_borregas/00000035.00000",
            channel=CyberRecordChannel.ROUTING_RESPONSE)

        routing_response = routing_responses[0]
        routing_request = routing_response.routing_request

        openscenario_private = routing_request_transformer.transform(
            routing_request)

        self.assert_proto_type_equal(openscenario_private, Private)

    def write_proto_pyobject_to_yaml(self, file_path, proto_pyobject):
        encoded_data = OpenScenarioEncoder.encode_proto_pyobject_to_yaml(
            proto_pyobject)
        with open(file_path, "w") as file:
            file.write(encoded_data)

    def assert_proto_type_equal(self, reflection_type, pb2_type):
        self.assertEqual(str(reflection_type.__class__), str(pb2_type))


if __name__ == '__main__':
    unittest.main()
