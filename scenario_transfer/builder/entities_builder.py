from openscenario_msgs import Entities
from scenario_transfer.builder import Builder


class EntitiesBuilder(Builder):
    """
    message Entities {
        repeated ScenarioObject scenarioObjects = 1;  // 0..*
        repeated EntitySelection entitySelections = 2;  // 0..*
    }
    """

    def __init__(self):
        pass

    def get_result(self) -> Entities:
        return Entities()
