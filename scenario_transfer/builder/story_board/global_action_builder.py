from typing import Optional
from openscenario_msgs import GlobalAction, Position, EntityAction, AddEntityAction, DeleteEntityAction
from scenario_transfer.builder import Builder


# // Message for GlobalAction
# message GlobalAction {
#     optional EnvironmentAction environmentAction = 1;  // 0..1
#     optional EntityAction entityAction = 2;  // 0..1
#     optional InfrastructureAction infrastructureAction = 3;  // 0..1
#     optional TrafficAction trafficAction = 4;  // 0..1
#     optional VariableAction variableAction = 5;  // 0..1
# }
class GlobalActionBuilder(Builder):
    product: GlobalAction
    entity_action: Optional[EntityAction]

    def __init__(self):
        pass

    def make_add_entity_action(self, entity_name: str, position: Position):
        self.entity_action = EntityAction(
            entityRef=entity_name,
            addEntityAction=AddEntityAction(position=position))

    def make_delete_entity_action(self, entity_name: str):
        self.entity_action = EntityAction(
            entityRef=entity_name, deleteEntityAction=DeleteEntityAction())

    def get_result(self):
        assert self.entity_action is not None

        if self.entity_action is not None:
            self.product = GlobalAction(entityAction=self.entity_action)

        return self.product
