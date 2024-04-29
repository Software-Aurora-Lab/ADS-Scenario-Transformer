from openscenario_msgs import CatalogLocations
from ads_scenario_transformer.builder import Builder


class CatalogLocationsBuilder(Builder):

    def __init__(self):
        pass

    def get_result(self) -> CatalogLocations:
        return CatalogLocations()