from typing import Dict
from scenario_transfer.builder import Builder
from openscenario_msgs import Actors, Entities, EntityRef


class ActorsBuilder(Builder):
    product: Actors

    _default_actors: Dict[str, Actors]
    name_key: str

    def __init__(self, entities: Entities, scenario_object_name: str):
        self.make_default_actors(entities=entities)
        self.scenario_object_name = scenario_object_name

    def make_default_actors(self, entities: Entities):
        default_actors = {}

        for scenario_object in entities.scenarioObjects:
            default_actors[scenario_object.name] = Actors(
                selectTriggeringEntities=False,
                entityRefs=[EntityRef(entityRef=scenario_object.name)])

        self._default_actors = default_actors

    def get_result(self):
        if self.scenario_object_name not in self._default_actors:
            raise ValueError("Actors not found from default actors")

        return self._default_actors[self.scenario_object_name]
