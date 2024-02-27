from openscenario_msgs import OpenScenarioCategory
from scenario_transfer.builder import Builder


class OpenScenarioCategoryBuilder(Builder):
    """
    message OpenScenarioCategory {
        required ScenarioDefinition scenarioDefinition = 1;  // 1..1
        required CatalogDefinition catalogDefinition = 2;    // 1..1
    }
    """

    def __init__(self):
        pass

    def get_result(self) -> OpenScenarioCategory:
        return OpenScenarioCategory()
