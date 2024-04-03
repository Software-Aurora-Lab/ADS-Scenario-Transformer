from typing import List
from openscenario_msgs import Init, InitActions, GlobalAction, UserDefinedAction, Private
from scenario_transfer import Builder


class InitBuilder(Builder):
    product: Init

    def __init__(self):
        self.init_actions_builder = InitActionsBuilder()
        
    def make_global_actions(self, global_actions: List[GlobalAction]):
        self.init_actions_builder.make_global_actions(global_actions)

    def make_user_defined_actions(self, user_defined_actions: List[UserDefinedAction]):
        self.init_actions_builder.make_user_defined_actions(user_defined_actions)

    def make_privates(self, privates: List[Private]):
        self.init_actions_builder.make_privates(privates)

    def get_result(self) -> Init:
        self.product = Init(actions=self.init_actions_builder.get_result())
        return self.product

class InitActionsBuilder(Builder):
    product: InitActions

    def __init__(self):
        self.global_actions = None
        self.user_defined_actions = None
        self.privates = None

    def make_global_actions(self, global_actions: List[GlobalAction]):
        self.global_actions = global_actions
        
    def make_user_defined_actions(self, user_defined_actions: List[UserDefinedAction]):
        self.user_defined_actions = user_defined_actions

    def make_privates(self, privates: List[Private]):
        self.privates = privates

    def get_result(self) -> InitActions:
        self.product = InitActions(
            globalActions=self.global_actions,
            userDefinedActions=self.user_defined_actions,
            privates=self.privates
        )
        return self.product

