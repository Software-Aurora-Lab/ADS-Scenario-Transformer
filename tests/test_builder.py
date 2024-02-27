import unittest
from datetime import datetime
from openscenario_msgs import CatalogDefinition, FileHeader
from scenario_transfer.builder import CatalogDefinitionBuilder, FileHeaderBuilder


class TestBuilder(unittest.TestCase):

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
