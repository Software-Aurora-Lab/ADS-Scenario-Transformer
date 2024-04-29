from enum import Enum
from openscenario_msgs import UserDefinedAction, CustomCommandAction
from ads_scenario_transformer.builder import Builder


class BuiltInUserDefinedActionType(Enum):
    EXIT_SUCCESS = 1
    EXIT_FAILURE = 2
    NULL = 3


class UserDefinedActionBuilder(Builder):
    product: UserDefinedAction

    def make_custom_command_action(self, type: str, content: str):
        self.product = UserDefinedAction(
            customCommandAction=CustomCommandAction(type=type,
                                                    content=content))

    def get_result(self) -> UserDefinedAction:
        return self.product

    @staticmethod
    def built_in_action(
            type: BuiltInUserDefinedActionType) -> UserDefinedAction:

        if type == BuiltInUserDefinedActionType.EXIT_SUCCESS:
            return UserDefinedAction(customCommandAction=CustomCommandAction(
                type="exitSuccess"))
        elif type == BuiltInUserDefinedActionType.EXIT_FAILURE:
            return UserDefinedAction(customCommandAction=CustomCommandAction(
                type="exitFailure"))
        # type == BuiltInUserDefinedActionType.NULL:
        return UserDefinedAction(customCommandAction=CustomCommandAction(
            type=":"))
