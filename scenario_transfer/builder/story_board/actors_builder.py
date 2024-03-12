from typing import Dict
from scenario_transfer.builder import Builder
from openscenario_msgs import Actors, Entities


class ActorsBuilder(Builder):
    product: Actors

    _default_actors: Dict[str, Actors]
    name_key: str

    def __init__(self, entities: Entities):
        self._default_actors = self.make_default_actors(entities=entities)
        self.name_key = ""

    def make_default_actors(self, entities: Entities) -> Dict[str, Actors]:
        default_actors = {}

        for scenario_object in entities.scenarioObjects:
            default_actors[scenario_object.name] = Actors(
                selectTriggeringEntities=False,
                entityRef=[scenario_object.name])

        return default_actors

    def set_key(self, name_key: str):
        self.name_key = name_key

    def get_result(self):
        if self.name_key in self._default_actors:
            return self._default_actors[self.name_key]
