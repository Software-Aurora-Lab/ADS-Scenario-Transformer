from openscenario_msgs import ScenarioDefinition
from scenario_transfer.builder import Builder


class ScenarioDefinitionBuilder(Builder):
    """
    message ScenarioDefinition {
        repeated ParameterDeclaration parameterDeclarations = 1;  // 0..*
        required CatalogLocations catalogLocations = 2;           // 1..1
        required RoadNetwork roadNetwork = 3;                     // 1..1
        required Entities entities = 4;                           // 1..1
        required Storyboard storyboard = 5;                       // 1..1
    }
    """

    def __init__(self):
        pass

    def get_result(self) -> ScenarioDefinition:
        return ScenarioDefinition()
