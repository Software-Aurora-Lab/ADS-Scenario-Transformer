import os
from typing import List, Optional
from enum import Enum
from dataclasses import dataclass
import yaml
import copy
from openscenario_msgs import Entities, ScenarioObject
from scenario_transformer.builder import Builder
from scenario_transformer.openscenario.openscenario_coder import OpenScenarioDecoder


class EntityType(Enum):
    EGO = "ego"
    NPC = "npc"
    PEDESTRIAN = "pedestrian"


@dataclass
class EntityMeta:
    entity_type: EntityType
    embedding_id: Optional[int] = None


class EntitiesBuilder(Builder):
    """
    - Check usage at test_builder.py
    
    message Entities {
        repeated ScenarioObject scenarioObjects = 1;  // 0..*
        repeated EntitySelection entitySelections = 2;  // 0..*
    }
    """

    product: Entities

    def __init__(self,
                 entities: List[EntityMeta] = [
                     EntityMeta(entity_type=EntityType.EGO)
                 ]):
        self.not_ego_label = 1
        self.load_default_scenario_objects(self.config_path())

        self.scenario_objects = self.make_default_scenario_objects(
            entities=entities)

    def config_path(self) -> str:
        directory = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(directory, 'entities.yaml')

    def load_default_scenario_objects(self, config_path: str):

        with open(config_path, 'r') as file:
            default_scenario_object_data = file.read()

        dict = yaml.safe_load(default_scenario_object_data)

        self.default_scenario_objects = {}

        entities = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict, type_=Entities, exclude_top_level_key=True)

        self.default_scenario_objects[
            EntityType.EGO.value] = entities.scenarioObjects[0]
        self.default_scenario_objects[
            EntityType.NPC.value] = entities.scenarioObjects[1]
        self.default_scenario_objects[
            EntityType.PEDESTRIAN.value] = entities.scenarioObjects[2]

    def make_default_scenario_objects(
            self, entities: List[EntityMeta]) -> List[ScenarioObject]:

        ego = None
        scenario_objects = []
        sorted_entities = sorted(entities, key=lambda x: x.entity_type.value)

        for entity_meta in sorted_entities:

            entity = copy.deepcopy(
                self.default_scenario_objects[entity_meta.entity_type.value])

            if entity_meta.entity_type == EntityType.EGO:
                ego = entity
            else:
                entity.name = f"{entity_meta.entity_type.value}_{self.not_ego_label}"
                if entity_meta.embedding_id:
                    entity.name = entity.name + f"_id_{entity_meta.embedding_id}"
                self.not_ego_label += 1
                scenario_objects.append(entity)

        return [ego] + scenario_objects if ego else scenario_objects

    def add_default_entity(self,
                           entity_type: EntityType,
                           id: Optional[int] = None):
        if entity_type == EntityType.EGO:
            return

        copied_entity = copy.deepcopy(
            self.default_scenario_objects[entity_type.value])
        copied_entity.name = f"{entity_type.value}_{self.not_ego_label}"
        self.not_ego_label += 1
        self.scenario_objects.append(copied_entity)

    def get_result(self) -> Entities:
        assert len(self.scenario_objects) > 0

        self.product = Entities(
            scenarioObjects=self.scenario_objects,
            entitySelections=[]  # Not in used
        )
        return self.product
