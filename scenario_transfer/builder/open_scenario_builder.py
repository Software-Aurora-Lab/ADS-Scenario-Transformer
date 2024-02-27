from openscenario_msgs import OpenScenario
from scenario_transfer.builder import Builder


class OpenScenarioBuilder(Builder):
    """
    message OpenScenario {
        required FileHeader fileHeader = 1;                      // 1..1
        required OpenScenarioCategory openScenarioCategory = 2;  // 1..1
    }
    """

    def __init__(self):
        pass

    def get_result(self) -> OpenScenario:
        return OpenScenario()
