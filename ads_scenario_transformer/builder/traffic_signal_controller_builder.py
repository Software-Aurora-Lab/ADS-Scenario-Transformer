from typing import List
from enum import Enum
from openscenario_msgs import TrafficSignalController, Phase, TrafficSignalState
from ads_scenario_transformer.builder import Builder


class TrafficLightbulbState(Enum):
    RED_ON_CIRCLE = "red solidOn circle"
    RED_OFF_CIRCLE = "red solidOff circle"
    YELLOW_ON_CIRCLE = "yellow solidOn circle"
    YELLOW_OFF_CIRCLE = "yellow solidOff circle"
    GREEN_ON_CIRCLE = "green solidOn circle"
    GREEN_OFF_CIRCLE = "green solidOff circle"


class TrafficSignalControllerBuilder(Builder):

    product: TrafficSignalController

    def __init__(self, name: str, phases: List[Phase] = []):
        self.product = TrafficSignalController(name=name, phases=phases)

    def add_phase(self, phase: Phase):
        self.product.phases.append(phase)

    def get_result(self) -> TrafficSignalController:
        return self.product


class PhaseBuilder(Builder):
    product: Phase

    def __init__(self, name: str, duration: float = float('inf')):
        self.name = name
        self.duration = duration
        self.states = []

    def add_state(self, state: TrafficLightbulbState):
        self.states.append(state)

    def get_result(self) -> Phase:
        self.product = Phase(name=self.name,
                             duration=self.duration,
                             trafficSignalStates=self.states)
        return self.product


class TrafficSignalStateBuilder(Builder):
    product: TrafficSignalState

    def make_state(self, id: str, state: TrafficLightbulbState):
        self.product = TrafficSignalState(trafficSignalId=id,
                                          state=state.value)

    def get_result(self) -> TrafficSignalState:
        assert self.product is not None
        return self.product
