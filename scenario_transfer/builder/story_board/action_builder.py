from typing import List, Optional
from openscenario_msgs import Action, GlobalAction, UserDefinedAction, PrivateAction
from scenario_transfer import Builder
from scenario_transfer.builder.story_board.global_action_builder import GlobalActionBuilder
from scenario_transfer.builder.story_board.private_action_builder import PrivateActionBuilder
from scenario_transfer.builder.story_board.routing_action_builder import RoutingActionBuilder


class ActionBuilder(Builder):
    product: Action

    def make_action(self,
                    name: str,
                    global_action: Optional[GlobalAction] = None,
                    user_defined_action: Optional[UserDefinedAction] = None,
                    private_action: Optional[PrivateAction] = None):
        if global_action is not None:
            self.product = Action(globalAction=global_action, name=name)
        elif user_defined_action is not None:
            self.product = Action(userDefinedAction=user_defined_action,
                                  name=name)
        elif private_action is not None:
            self.product = Action(privateAction=private_action, name=name)
        else:
            raise ValueError(
                "Action needs one of the following: globalAction, userDefinedAction, privateAction"
            )

    def get_result(self) -> Action:
        return self.product
