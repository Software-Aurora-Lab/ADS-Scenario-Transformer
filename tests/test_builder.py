import unittest
import yaml
from datetime import datetime
from definitions import TEST_ROOT
from openscenario_msgs import CatalogDefinition, FileHeader, Entities, ParameterDeclarations, ParameterDeclaration, ScenarioDefinition, Route, Private, ScenarioObject, TeleportAction, RoutingAction, AssignRouteAction, AcquirePositionAction
from openscenario_msgs.scenario_pb2 import Scenario, OpenSCENARIO

from scenario_transfer.builder import CatalogDefinitionBuilder, FileHeaderBuilder, EntitiesBuilder, ParameterDeclarationsBuilder, RoadNetworkBuilder, TrafficSignalControllerBuilder, TrafficSignalStateBuilder, ScenarioDefinitionBuilder, PrivateBuilder

from scenario_transfer.builder.scenario_builder import ScenarioConfiguration, ScenarioBuilder
from scenario_transfer.builder.entities_builder import EntityType
from scenario_transfer.builder.road_network_builder import RoadNetworkBuilder
from scenario_transfer.openscenario import OpenScenarioEncoder, OpenScenarioDecoder


class TestBuilder(unittest.TestCase):

    def setUp(self):
        self.route_file_path = TEST_ROOT + "/data/openscenario_route.yaml"

    def test_scenario_builder(self):

        configuration = ScenarioConfiguration(
            entities=[EntityType.EGO, EntityType.NPC],
            lanelet_map_path="/home/user/lanelet_map.osm")

        builder = ScenarioBuilder(scenario_configuration=configuration)

        builder.make_file_header()
        builder.make_scenario_definition()
        builder.make_scenario_modifiers()
        builder.make_scenario_definition()
        scenario = builder.get_result()

        self.assert_proto_type_equal(scenario, Scenario)
        self.assert_proto_type_equal(scenario.openScenario, OpenSCENARIO)
        self.assert_proto_type_equal(scenario.openScenario.fileHeader,
                                     FileHeader)

    def test_entities_builder(self):
        builder = EntitiesBuilder(entities=[
            EntityType.NPC, EntityType.NPC, EntityType.EGO,
            EntityType.PEDESTRIAN, EntityType.NPC
        ])

        builder.add_default_entity(EntityType.NPC)

        entities = builder.get_result()
        self.assertIsInstance(entities, Entities)
        self.assertEqual(len(entities.scenarioObjects), 6)
        self.assertEqual(entities.scenarioObjects[0].name, "ego")
        self.assertEqual(entities.scenarioObjects[1].name, "npc_1")
        self.assertEqual(entities.scenarioObjects[2].name, "npc_2")
        self.assertEqual(entities.scenarioObjects[3].name, "npc_3")
        self.assertEqual(entities.scenarioObjects[4].name, "pedestrian_4")
        self.assertEqual(entities.scenarioObjects[5].name, "npc_5")

    def test_file_header_builder(self):
        builder = FileHeaderBuilder()
        file_header = builder.get_result()
        self.assertIsInstance(file_header, FileHeader)

        expected_format = '%Y-%m-%dT%H:%M:%S'
        try:
            datetime.strptime(file_header.date, expected_format)
        except ValueError:
            self.fail(f"Date format should be {expected_format}")
        self.assertEqual(file_header.description, "Default FileHeader")
        self.assertEqual(file_header.author, "ADS Scenario Tranferrer")

    def test_catalog_definition_builder(self):
        builder = CatalogDefinitionBuilder()
        catalog_definition = builder.get_result()
        self.assertIsInstance(catalog_definition, CatalogDefinition)

    def test_parameter_declarations_builder(self):

        declarations = [
            ParameterDeclaration(name="__ego_dimensions_length__",
                                 parameterType=2,
                                 value='0'),
            ParameterDeclaration(name="__ego_dimensions_width__",
                                 parameterType=2,
                                 value='0')
        ]

        builder = ParameterDeclarationsBuilder(
            parameterDeclarations=declarations)
        parameter_declarations = builder.get_result()
        self.assertIsInstance(parameter_declarations, ParameterDeclarations)
        self.assertEqual(len(parameter_declarations.parameterDeclarations), 2)

    def test_road_network_builder(self):
        controller_builder = TrafficSignalControllerBuilder(
            name="StraghtSignal")
        state_builder = TrafficSignalStateBuilder(
            id_states=[('12515',
                        "red;solidOn;circle"), ('12504',
                                                "red;solidOn;circle")])
        controller_builder.add_phase(name="RED",
                                     states=state_builder.get_result())

        state_builder = TrafficSignalStateBuilder(id_states=[(
            '12515', "green;solidOn;circle"), ('12504',
                                               "green;solidOn;circle")])

        controller_builder.add_phase(name="RED",
                                     states=state_builder.get_result())

        builder = RoadNetworkBuilder(
            lanelet_map_path="/home/users/lanelet_map.osm",
            trafficSignalControllers=[controller_builder.get_result()])

        road_network = builder.get_result()

        self.assertEqual(road_network.logicFile.filepath,
                         "/home/users/lanelet_map.osm")
        self.assertEqual(
            len(road_network.trafficSignals.trafficSignalControllers), 1)

        traffic_signal = road_network.trafficSignals.trafficSignalControllers[
            0]

        self.assertEqual(len(traffic_signal.phases), 2)

        self.assertEqual(traffic_signal.phases[0].name, "RED")
        self.assertEqual(
            traffic_signal.phases[1].trafficSignalStates[0].trafficSignalId,
            "12515")

    def test_scenario_definition_builder(self):
        parameter_declarations = [
            ParameterDeclaration(name="__ego_dimensions_length__",
                                 parameterType=2,
                                 value='0'),
            ParameterDeclaration(name="__ego_dimensions_width__",
                                 parameterType=2,
                                 value='0')
        ]

        builder = ScenarioDefinitionBuilder(
            parameter_declarations=parameter_declarations)

        builder.make_road_network(lanelet_map_path="lanelet_map.osm")
        builder.make_default_entities(entities=[
            EntityType.EGO, EntityType.NPC, EntityType.NPC,
            EntityType.PEDESTRIAN
        ])
        builder.make_storyboard()
        scenario_definition = builder.get_result()

        self.assertIsInstance(scenario_definition, ScenarioDefinition)
        self.assertIsNotNone(scenario_definition.roadNetwork)
        self.assertIsNotNone(scenario_definition.catalogLocations)
        self.assertIsNotNone(scenario_definition.entities)
        self.assertIsNotNone(scenario_definition.storyboard)

    def test_private_builder(self):
        with open(self.route_file_path, 'r') as file:
            input = file.read()

        dict = yaml.safe_load(input)

        openscenario_route = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict, type_=Route, exclude_top_level_key=True)

        entities_builder = EntitiesBuilder(entities=[EntityType.EGO])
        ego = entities_builder.get_result().scenarioObjects[0]

        self.assert_proto_type_equal(openscenario_route, Route)
        self.assert_proto_type_equal(ego, ScenarioObject)

        private_builder = PrivateBuilder(
            waypoints=openscenario_route.waypoints)
        private_builder.make_entity(ego)
        private_builder.make_teleport_action()
        private_builder.make_routing_action()

        openscenario_private = private_builder.get_result()

        self.assertIsInstance(openscenario_private, Private,
                              "The private should be of type Private")

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

        end_waypoint = routing_action.assignRouteAction.route.waypoints[-1]
        end_lane_position = end_waypoint.position.lanePosition

        self.assertEqual(end_lane_position.laneId, "149")
        self.assertEqual(end_lane_position.offset, 1.4604610803960605)
        self.assertEqual(end_lane_position.s, 26.739416492972932)
        self.assertEqual(end_lane_position.orientation.h, -1.9883158777364047)

    def assert_proto_type_equal(self, reflection_type, pb2_type):
        self.assertEqual(str(reflection_type.__class__), str(pb2_type))

    def write_proto_pyobject_to_yaml(self, file_path, proto_pyobject,
                                     wrap_result_with_typename):
        encoded_data = OpenScenarioEncoder.encode_proto_pyobject_to_yaml(
            proto_pyobject, wrap_result_with_typename)

        with open(file_path, "w") as file:
            file.write(encoded_data)


if __name__ == '__main__':
    unittest.main()
