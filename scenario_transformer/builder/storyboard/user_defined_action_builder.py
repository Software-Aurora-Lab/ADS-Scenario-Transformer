from openscenario_msgs import UserDefinedAction, CustomCommandAction
from scenario_transformer.builder import Builder


class UserDefinedActionBuilder(Builder):
    product: UserDefinedAction

    def make_custom_command_action(self, type: str, content: str):
        self.product = UserDefinedAction(
            customCommandAction=CustomCommandAction(type=type,
                                                    content=content))

    def get_result(self) -> UserDefinedAction:
        return self.product
