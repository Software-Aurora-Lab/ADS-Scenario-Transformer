from typing import Optional
from openscenario_msgs import GlobalAction, Position, EntityAction, AddEntityAction, DeleteEntityAction, InfrastructureAction
from openscenario_msgs.traffic_signal_pb2 import TrafficSignalAction, TrafficSignalStateAction, TrafficSignalControllerAction
from scenario_transformer.builder import Builder


class GlobalActionBuilder(Builder):
    product: GlobalAction
    entity_action: Optional[EntityAction]
    infrastructure_action: Optional[InfrastructureAction]

    def __init__(self):
        self.entity_action = None
        self.infrastructure_action = None

    def make_add_entity_action(self, entity_name: str, position: Position):
        self.entity_action = EntityAction(
            entityRef=entity_name,
            addEntityAction=AddEntityAction(position=position))

    def make_delete_entity_action(self, entity_name: str):
        self.entity_action = EntityAction(
            entityRef=entity_name, deleteEntityAction=DeleteEntityAction())

    def make_traffic_signal_controller_action(
            self, phase: str, traffic_signal_controller_name: str):
        traffic_signal_controller_action = TrafficSignalControllerAction(
            phase=phase,
            trafficSignalControllerRef=traffic_signal_controller_name)

        traffic_signal_action = TrafficSignalAction(
            trafficSignalControllerAction=traffic_signal_controller_action)
        self.infrastructure_action = InfrastructureAction(
            trafficSignalAction=traffic_signal_action)

    def make_traffic_signal_state_action(self, name: str, state: str):
        traffic_signal_state_action = TrafficSignalStateAction(name=name,
                                                               state=state)
        traffic_signal_action = TrafficSignalAction(
            trafficSignalStateAction=traffic_signal_state_action)
        self.infrastructure_action = InfrastructureAction(
            trafficSignalAction=traffic_signal_action)

    def get_result(self):
        assert self.entity_action is not None or self.infrastructure_action is not None

        if self.entity_action is not None:
            self.product = GlobalAction(entityAction=self.entity_action)
        elif self.infrastructure_action is not None:
            self.product = GlobalAction(
                infrastructureAction=self.infrastructure_action)

        return self.product
