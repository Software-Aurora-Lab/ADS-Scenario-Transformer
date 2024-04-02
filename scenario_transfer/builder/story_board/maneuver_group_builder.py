from typing import List, Optional
from openscenario_msgs import ManeuverGroup, Maneuver, Actors
from scenario_transfer import Builder


class ManeuverGroupBuilder(Builder):
    product: ManeuverGroup

    def __init__(self, 
                 name: str = "",
                 maximum_execution_count: int = 1):
        self.name = name
        self.maximum_execution_count = maximum_execution_count

    def make_actors(self, actors: Actors):
        self.actors = actors
        
    def make_maneuvers(self, maneuvers: List[Maneuver]):
        self.maneuvers = maneuvers

    def get_result(self) -> Maneuver:
        self.product = ManeuverGroup(
            name=self.name,
            maximumExecutionCount=self.maximum_execution_count,
            actors=self.actors,
            maneuvers=self.maneuvers)
        
        return self.product