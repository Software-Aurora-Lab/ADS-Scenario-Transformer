from openscenario_msgs import CatalogLocations
from scenario_transfer.builder import Builder


class CatalogLocationsBuilder(Builder):

    def __init__(self):
        pass

    def get_result(self) -> CatalogLocations:
        return CatalogLocations()
