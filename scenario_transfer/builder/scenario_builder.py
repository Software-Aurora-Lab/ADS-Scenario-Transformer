from typing import List
from openscenario_msgs import Scenario, ScenarioDefinition, ScenarioModifiers, FileHeader, TrafficSignalController, OpenSCENARIO
from scenario_transfer.builder import Builder
from scenario_transfer.builder import scenario_definition_builder
from scenario_transfer.builder.file_header_builder import FileHeaderBuilder
from scenario_transfer.builder.scenario_definition_builder import ScenarioDefinitionBuilder
from scenario_transfer.builder.entities_builder import EntitiesBuilder, EntityType


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

    def make_scenario_modifiers(self):
        self.scenario_modifiers = ScenarioModifiers()

    def make_file_header(self):
        self.header = FileHeaderBuilder().get_result()

    def make_scenario_definition(self):
        scenario_definition_builder = ScenarioDefinitionBuilder()

        scenario_definition_builder.make_default_entities(
            self.configuration.entities)
        scenario_definition_builder.make_road_network(
            lanelet_map_path=self.configuration.lanelet_map_path,
            pcd_map_path=self.configuration.pcd_map_path,
            trafficSignals=self.configuration.traffic_signals)
        scenario_definition_builder.make_storyboard()

        self.scenario_definition = scenario_definition_builder.get_result()

    def get_result(self) -> Scenario:
        assert self.header is not None
        assert self.scenario_modifiers is not None
        assert self.scenario_definition is not None

        self.open_scenario = OpenSCENARIO(
            fileHeader=self.header,
            parameterDeclarations=self.scenario_definition.
            parameterDeclarations,
            catalogLocations=self.scenario_definition.catalogLocations,
            roadNetwork=self.scenario_definition.roadNetwork,
            entities=self.scenario_definition.entities,
            storyboard=self.scenario_definition.storyboard)

        self.product = Scenario(scenarioModifiers=self.scenario_modifiers,
                                openScenario=self.open_scenario)

        return self.product
