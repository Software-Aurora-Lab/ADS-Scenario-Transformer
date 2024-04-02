from typing import List, Optional
from openscenario_msgs import Maneuver, Event, ParameterDeclaration
from scenario_transfer import Builder


class ManeuverBuilder(Builder):
    product: Maneuver

    def __init__(self, name: str):
        self.name = name

    def make_events(self, 
                    events: List[Event], 
                    parameter_declarations: List[ParameterDeclaration]=[]):
        self.product = Maneuver(name=self.name,
                                parameterDeclarations=parameter_declarations,
                                events=events)
        
    def get_result(self) -> Maneuver:
        assert len(self.product.events) > 0, "Maneuver needs at least one event"
        return self.product