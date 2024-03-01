import unittest
from datetime import datetime
from openscenario_msgs import CatalogDefinition, FileHeader, Entities, ParameterDeclarations, ParameterDeclaration, ScenarioDefinition
from scenario_transfer.builder import CatalogDefinitionBuilder, FileHeaderBuilder, EntitiesBuilder, ParameterDeclarationsBuilder, RoadNetworkBuilder, TrafficSignalControllerBuilder, TrafficSignalStateBuilder, ScenarioDefinitionBuilder
from scenario_transfer.builder.entities_builder import EntityType
from scenario_transfer.builder.road_network_builder import RoadNetworkBuilder


class TestBuilder(unittest.TestCase):

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
        self.assertEqual(file_header.author, "ADS Scenario Tranferer")

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
            trafficSignals=[controller_builder.get_result()])

        road_network = builder.get_result()

        self.assertEqual(road_network.logicFile.filepath,
                         "/home/users/lanelet_map.osm")
        self.assertEqual(len(road_network.trafficSignals), 1)

        traffic_signal = road_network.trafficSignals[0]

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


if __name__ == '__main__':
    unittest.main()
