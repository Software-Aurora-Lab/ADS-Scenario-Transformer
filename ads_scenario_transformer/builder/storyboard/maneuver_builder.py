from typing import List, Optional
from openscenario_msgs import Maneuver, Event, ParameterDeclaration
from ads_scenario_transformer.builder import Builder


class ManeuverBuilder(Builder):
    product: Maneuver

    def __init__(self,
                 name: str = "",
                 parameter_declarations: List[ParameterDeclaration] = []):
        self.name = name
        self.parameter_declarations = parameter_declarations
        self.events=[]

    def add_event(self, event: Event):
        self.events.append(event)
        
    def make_events(self, events: List[Event]):
        self.events = events
        
    def get_result(self) -> Maneuver:
        assert len(self.events) > 0, "Maneuver needs at least one event"

        self.product = Maneuver(
            name=self.name,
            parameterDeclarations=self.parameter_declarations,
            events=self.events)
        
        return self.product
