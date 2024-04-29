from typing import Optional
from openscenario_msgs import Action, GlobalAction, UserDefinedAction, PrivateAction
from ads_scenario_transformer.builder import Builder
from ads_scenario_transformer.builder.storyboard.user_defined_action_builder import BuiltInUserDefinedActionType, UserDefinedActionBuilder


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

    def make_built_in_user_defined_action(self,
                                          type: BuiltInUserDefinedActionType):
        action = UserDefinedActionBuilder.built_in_action(type=type)
        self.product = Action(userDefinedAction=action)

    def get_result(self) -> Action:
        return self.product
