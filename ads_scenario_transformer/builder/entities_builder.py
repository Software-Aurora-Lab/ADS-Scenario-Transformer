from typing import List, Optional, Set
from enum import Enum
from dataclasses import dataclass
import yaml
import copy
from definitions import DEFAULT_ENTITIES_PATH
from openscenario_msgs import Entities, BoundingBox, Center, Dimensions
from ads_scenario_transformer.builder import Builder
from ads_scenario_transformer.openscenario.openscenario_coder import OpenScenarioDecoder


class ASTEntityType(Enum):
    EGO = "ego"
    CAR = "car"
    BICYCLE = "bicycle"
    PEDESTRIAN = "pedestrian"

    # ref: https://github.com/fzi-forschungszentrum-informatik/Lanelet2/blob/master/lanelet2_core/doc/LaneletAndAreaTagging.md#subtype-and-location
    def available_lanelet_subtype(self) -> Set[str]:
        if self == ASTEntityType.EGO or ASTEntityType.CAR:
            return set(["road", "highway", "play_street", "exit"])
        elif self == ASTEntityType.BICYCLE:
            return set(["road", "play_street", "bicycle_lane"])
        elif self == ASTEntityType.PEDESTRIAN:
            return set([
                "crosswalk", "stairs", "walkway", "shared_walkway",
                "play_street", "exit"
            ])
        return set()


@dataclass(frozen=True)
class ASTEntity:
    entity_type: ASTEntityType
    use_default_scenario_object: bool
    embedding_id: Optional[int] = None
    length: Optional[float] = None
    height: Optional[float] = None
    width: Optional[float] = None


class EntitiesBuilder(Builder):
    """
    - Check usage at test_builder.py
    
    message Entities {
        repeated ScenarioObject scenarioObjects = 1;  // 0..*
        repeated EntitySelection entitySelections = 2;  // 0..*
    }
    """

    product: Entities

    def __init__(self):
        self.not_ego_label = 1
        self.load_default_scenario_objects(DEFAULT_ENTITIES_PATH)
        self.scenario_objects = []
        self.make_ego_scenario_object()

    def make_ego_scenario_object(self):
        ego_scenario_obj = self.default_scenario_objects[
            ASTEntityType.EGO.value]
        self.scenario_objects.append(
            (ASTEntity(entity_type=ASTEntityType.EGO,
                       use_default_scenario_object=True), ego_scenario_obj))

    def load_default_scenario_objects(self, config_path: str):

        with open(config_path, 'r') as file:
            default_scenario_object_data = file.read()

        dict = yaml.safe_load(default_scenario_object_data)

        self.default_scenario_objects = {}

        entities = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict, type_=Entities, exclude_top_level_key=True)

        self.default_scenario_objects[
            ASTEntityType.EGO.value] = entities.scenarioObjects[0]
        self.default_scenario_objects[
            ASTEntityType.CAR.value] = entities.scenarioObjects[1]
        self.default_scenario_objects[
            ASTEntityType.BICYCLE.value] = entities.scenarioObjects[2]
        self.default_scenario_objects[
            ASTEntityType.PEDESTRIAN.value] = entities.scenarioObjects[3]

    def add_default_entity(self, ast_entity: ASTEntity):
        if ast_entity.entity_type == ASTEntityType.EGO:
            return

        copied_entity = copy.deepcopy(
            self.default_scenario_objects[ast_entity.entity_type.value])
        copied_entity.name = f"{ast_entity.entity_type.value}_{self.not_ego_label}"
        if ast_entity.embedding_id:
            copied_entity.name = copied_entity.name + f"_id_{ast_entity.embedding_id}"

        self.not_ego_label += 1
        self.scenario_objects.append((ast_entity, copied_entity))

    def add_entity(self, ast_entity: ASTEntity):
        if ast_entity.use_default_scenario_object:
            self.add_default_entity(ast_entity=ast_entity)
            return

        copied_entity = copy.deepcopy(
            self.default_scenario_objects[ast_entity.entity_type.value])

        copied_entity.name = f"{ast_entity.entity_type.value}_{self.not_ego_label}"
        if ast_entity.embedding_id:
            copied_entity.name = copied_entity.name + f"_id_{ast_entity.embedding_id}"

        bounding_box = BoundingBox(
            center=self.get_default_center(ast_entity.entity_type),
            dimensions=Dimensions(height=round(ast_entity.height, 3),
                                  width=round(ast_entity.width, 3),
                                  length=round(ast_entity.length, 3)))

        if ast_entity.entity_type == ASTEntityType.PEDESTRIAN:
            copied_entity.entityObject.pedestrian.boundingBox.CopyFrom(
                bounding_box)
        else:
            copied_entity.entityObject.vehicle.boundingBox.CopyFrom(
                bounding_box)

        self.not_ego_label += 1
        self.scenario_objects.append((ast_entity, copied_entity))

    def get_default_center(self, entity_type: ASTEntityType) -> Center:
        if entity_type == ASTEntityType.CAR:
            return Center(x=1.355, y=0, z=1.25)
        elif entity_type == ASTEntityType.BICYCLE:
            return Center(x=0, y=0, z=1.25)
        elif entity_type == ASTEntityType.PEDESTRIAN:
            return Center(x=0, y=0, z=1)
        return Center(x=0, y=0, z=0)

    def get_result(self) -> Entities:
        assert len(self.scenario_objects) > 0

        self.product = Entities(
            scenarioObjects=[obj for ast_entity, obj in self.scenario_objects],
            entitySelections=[]  # Not in used
        )
        return self.product
