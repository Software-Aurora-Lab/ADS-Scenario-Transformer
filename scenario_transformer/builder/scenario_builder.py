from typing import List, Optional, Dict
from openscenario_msgs import Scenario, ScenarioDefinition, ScenarioModifiers, FileHeader, TrafficSignalController, OpenSCENARIO, Storyboard, ParameterDeclaration
from scenario_transformer.builder import Builder
from scenario_transformer.builder.file_header_builder import FileHeaderBuilder
from scenario_transformer.builder.scenario_definition_builder import ScenarioDefinitionBuilder
from scenario_transformer.builder.entities_builder import EntityType


class ScenarioConfiguration:
    entities: List[EntityType]
    lanelet_map_path: str
    pcd_map_path: str
    traffic_signals: List[TrafficSignalController]

    def __init__(self,
                 entities: List[EntityType],
                 lanelet_map_path: str,
                 pcd_map_path: str = "point_cloud.pcd",
                 traffic_signals: List[TrafficSignalController] = []):
        self.entities = entities
        self.lanelet_map_path = lanelet_map_path
        self.pcd_map_path = pcd_map_path
        self.traffic_signals = traffic_signals


class ScenarioBuilder(Builder):

    product: Scenario
    configuration: ScenarioConfiguration
    header: FileHeader
    scenario_modifiers: ScenarioModifiers
    scenario_definition: ScenarioDefinition
    open_scenario: OpenSCENARIO

    def __init__(self, scenario_configuration: ScenarioConfiguration):
        self.configuration = scenario_configuration
        self.scenario_modifiers = None
        self.header = None
        self.scenario_definition = None
        self.open_scenario = None

    def make_scenario_modifiers(self):
        self.scenario_modifiers = ScenarioModifiers()  # not in used

    def make_file_header(self, fileheader_dict: Optional[Dict] = None):
        if fileheader_dict:
            self.header = FileHeaderBuilder(dict=fileheader_dict).get_result()
        else:
            self.header = FileHeaderBuilder().get_result()

    def make_scenario_definition(
            self,
            storyboard: Storyboard,
            parameter_declarataions: List[ParameterDeclaration] = []):
        scenario_definition_builder = ScenarioDefinitionBuilder(
            parameter_declarations=parameter_declarataions)

        scenario_definition_builder.make_default_entities(
            self.configuration.entities)
        scenario_definition_builder.make_road_network(
            lanelet_map_path=self.configuration.lanelet_map_path,
            pcd_map_path=self.configuration.pcd_map_path,
            trafficSignals=self.configuration.traffic_signals)
        scenario_definition_builder.make_storyboard(storyboard=storyboard)

        self.scenario_definition = scenario_definition_builder.get_result()

    def get_open_scenario(self) -> OpenSCENARIO:
        assert self.header is not None
        assert self.scenario_modifiers is not None
        assert self.scenario_definition is not None

        if not self.open_scenario:
            self.open_scenario = OpenSCENARIO(
                fileHeader=self.header,
                parameterDeclarations=self.scenario_definition.
                parameterDeclarations,
                catalogLocations=self.scenario_definition.catalogLocations,
                roadNetwork=self.scenario_definition.roadNetwork,
                entities=self.scenario_definition.entities,
                storyboard=self.scenario_definition.storyboard)
        return self.open_scenario

    def get_result(self) -> Scenario:
        if not self.scenario_modifiers:
            self.make_scenario_modifiers()
        if not self.header:
            self.make_file_header()

        assert self.scenario_definition is not None

        open_scenario = self.get_open_scenario()
        self.product = Scenario(scenarioModifiers=self.scenario_modifiers,
                                openScenario=open_scenario)

        return self.product
