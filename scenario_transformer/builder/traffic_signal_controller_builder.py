from typing import List
from openscenario_msgs import TrafficSignalController, Phase, TrafficSignalState
from scenario_transformer.builder import Builder


class TrafficSignalControllerBuilder(Builder):

    product: TrafficSignalController

    def __init__(self, name: str, phases: List[Phase] = []):
        self.product = TrafficSignalController(name=name, phases=phases)

    def add_phase(self,
                  name: str,
                  states: [TrafficSignalState],
                  duration: int = float('inf')):
        phase = Phase(name=name, duration=duration, trafficSignalStates=states)
        self.product.phases.append(phase)

    def get_result(self) -> TrafficSignalController:
        return self.product


class TrafficSignalStateBuilder(Builder):
    """
    state: State of the signal, e.g. the visual information "off;off;on"
    """
    product: [TrafficSignalState]

    def __init__(self, id_states: [(str, str)]):

        self.product = [
            TrafficSignalState(trafficSignalId=id, state=state)
            for id, state in id_states
        ]

    def get_result(self) -> TrafficSignalState:
        return self.product
