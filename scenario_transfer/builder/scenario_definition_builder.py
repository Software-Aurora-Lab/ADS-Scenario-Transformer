from typing import List
from openscenario_msgs import ScenarioDefinition, ParameterDeclaration, RoadNetwork, Entities, Storyboard, TrafficSignalController
from scenario_transfer.builder import Builder, ParameterDeclarationBuilder, CatalogLocationsBuilder, RoadNetworkBuilder
from scenario_transfer.builder.entities_builder import EntitiesBuilder, EntityType
from openscenario_msgs import Init, InitActions  # TODO: Remove after implement Storyboard builder


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

    product: ScenarioDefinition
    parameter_declarations: List[ParameterDeclaration]
    road_network: RoadNetwork
    entities: Entities
    storyboard: Storyboard

    def __init__(self,
                 parameter_declarations: List[ParameterDeclaration] = []):
        self.parameter_declarations = parameter_declarations

    def add_parameter_declaration(self, name: str, parameterType: int,
                                  value: str):
        param = ParameterDeclarationBuilder(name, parameterType,
                                            value).get_result()
        self.parameter_declarations.append(param)

    def make_road_network(self,
                          lanelet_map_path: str,
                          pcd_map_path: str = "point_cloud.pcd",
                          trafficSignals: List[TrafficSignalController] = []):
        builder = RoadNetworkBuilder(lanelet_map_path, pcd_map_path,
                                     trafficSignals)
        self.road_network = builder.get_result()

    def make_default_entities(self, entities: [EntityType]):
        builder = EntitiesBuilder(entities=entities)
        self.entities = builder.get_result()

    def make_storyboard(self):  # TODO: fix this
        self.storyboard = Storyboard(init=Init(actions=InitActions(
            privates=[])))

    def get_result(self) -> ScenarioDefinition:
        assert self.road_network is not None
        assert self.entities is not None
        assert self.storyboard is not None
        
        self.product = ScenarioDefinition(
            parameterDeclarations=self.parameter_declarations,
            catalogLocations=CatalogLocationsBuilder().get_result(),
            roadNetwork=self.road_network,
            entities=self.entities,
            storyboard=self.storyboard)
        return self.product
