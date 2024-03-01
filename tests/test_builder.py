import unittest
from datetime import datetime
from openscenario_msgs import CatalogDefinition, FileHeader, Entities
from scenario_transfer.builder import CatalogDefinitionBuilder, FileHeaderBuilder, EntitiesBuilder
from scenario_transfer.builder.entities_builder import EntityType


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


if __name__ == '__main__':
    unittest.main()
