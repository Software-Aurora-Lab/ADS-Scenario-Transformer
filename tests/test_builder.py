import unittest

from openscenario_msgs import CatalogDefinition
from scenario_transfer.builder import CatalogDefinitionBuilder


class TestBuilder(unittest.TestCase):

    def test_catalog_definition_builder(self):
        catalog_definition_builder = CatalogDefinitionBuilder()
        catalog_definition = catalog_definition_builder.get_result()
        self.assertIsInstance(catalog_definition, CatalogDefinition)


if __name__ == '__main__':
    unittest.main()
