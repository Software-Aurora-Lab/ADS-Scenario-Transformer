from scenario_transformer.builder import Builder
from openscenario_msgs import Actors, EntityRef


class ActorsBuilder(Builder):
    product: Actors

    def __init__(self):
        self.entityRefs = []

    def add_entity_ref(self, scenario_object_name: str):
        self.entityRefs.append(EntityRef(entityRef=scenario_object_name))

    def get_result(self):
        self.product = Actors(selectTriggeringEntities=False,
                              entityRefs=self.entityRefs)
        return self.product
