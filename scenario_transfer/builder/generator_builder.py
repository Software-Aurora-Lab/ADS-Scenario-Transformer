import json
from openscenario_msgs import OpenScenario, OpenScenarioCategory, ScenarioDefinition, CatalogDefinition, FileHeader, ParameterDeclaration, CatalogLocation, RoadNetwork, Entities, Storyboard


# // Message for FileHeader
# message FileHeader {
#     required uint32 revMajor = 1;                   // 1..1
#     required uint32 revMinor = 2;                   // 1..1
#     required string date = 3;                       // 1..1, YYYY-MM-DDThh:mm:ss
#     required string description = 4;                // 1..1
#     required string author = 5;                     // 1..1
# }

class OpenScenarioBuilder:

    # message OpenScenario {
    #     required FileHeader fileHeader = 1;                      // 1..1
    #     required OpenScenarioCategory openScenarioCategory = 2;  // 1..1
    # }
    def build_open_scenario(self) -> OpenScenario:
        parts = [self.build_fileheader(), self.build_open_scenario_category()]
        return OpenScenario(fileHeader=parts[0], openScenarioCategory=parts[1])

    # // Message for OpenScenarioCategory
    # message OpenScenarioCategory {
    #     required ScenarioDefinition scenarioDefinition = 1;  // 1..1
    #     required CatalogDefinition catalogDefinition = 2;    // 1..1
    # }
    def build_open_scenario_category(self) -> OpenScenarioCategory:
        return OpenScenarioCategory(
            scenarioDefinition=self.build_scenario_definition(),
            catalogDefinition=self.build_catalog_definition())

    # // Message for ScenarioDefinition
    # message ScenarioDefinition {
    #     repeated ParameterDeclaration parameterDeclarations = 1;  // 0..*
    #     required CatalogLocations catalogLocations = 2;           // 1..1
    #     required RoadNetwork roadNetwork = 3;                     // 1..1
    #     required Entities entities = 4;                           // 1..1
    #     required Storyboard storyboard = 5;                       // 1..1
    # }
    def build_scenario_definition(self) -> ScenarioDefinition:
        return ScenarioDefinition(
            parameterDeclarations=self.build_parameter_declarations(),
            catalogLocations=self.build_catalog_locations(),
            roadNetwork=self.build_road_network(),
            entities=self.build_entities(),
            storyboard=self.build_storyboard())
class OpenScenarioBuilder:
    def __init__(self):
        pass

    def build_open_scenario(self) -> OpenScenario:
        return OpenScenario()


class OpenScenarioCategoryBuilder:
    def __init__(self):
        pass

    def build_open_scenario_category(self) -> OpenScenarioCategory:
        return OpenScenarioCategory()


class CatalogDefinitionBuilder:
    def __init__(self):
        pass

    def build_catalog_definition(self) -> CatalogDefinition:
        return CatalogDefinition()


class FileHeaderBuilder:
    def __init__(self):
        pass

    def build_fileheader(self) -> FileHeader:
        return FileHeader()


class ParameterDeclarationBuilder:
    def __init__(self):
        pass

    def build_parameter_declarations(self) -> ParameterDeclaration:
        return ParameterDeclaration()


class CatalogLocationBuilder:
    def __init__(self):
        pass

    def build_catalog_locations(self) -> CatalogLocation:
        return CatalogLocation()


class RoadNetworkBuilder:
    def __init__(self):
        pass

    def build_road_network(self) -> RoadNetwork:
        return RoadNetwork()


class EntitiesBuilder:
    def __init__(self):
        pass

    def build_entities(self) -> Entities:
        return Entities()


class StoryboardBuilder:
    def __init__(self):
        pass

    def build_storyboard(self) -> Storyboard:
        return Storyboard()



# // Message for CatalogDefinition
# message CatalogDefinition {
#     required Catalog catalog = 1;  // 1..1
# }

# // Message for Catalog
# message Catalog {
#     optional string name = 1;  // 0..1
#     repeated Vehicle vehicles = 2;  // 0..*
#     repeated Controller controllers = 3;  // 0..*
#     repeated Pedestrian pedestrians = 4;  // 0..*
#     repeated MiscObject miscObjects = 5;  // 0..*
#     repeated Environment environments = 6;  // 0..*
#     repeated Maneuver maneuvers = 7;  // 0..*
#     repeated Trajectory trajectories = 8;  // 0..*
#     repeated Route routes = 9;  // 0..*
# }
# // Message for Entities
# message Entities {
#     repeated ScenarioObject scenarioObjects = 1;  // 0..*
#     repeated EntitySelection entitySelections = 2;  // 0..*
# }
class Input<T: Dict>:
    use_default: bool
    data: T