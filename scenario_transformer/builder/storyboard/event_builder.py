from typing import List
from openscenario_msgs import Event, Action, Condition, Priority, GlobalAction, UserDefinedAction, PrivateAction
from scenario_transformer.builder import Builder
from scenario_transformer.builder.storyboard.action_builder import ActionBuilder
from scenario_transformer.builder.storyboard.trigger_builder import StartTriggerBuilder


class EventBuilder(Builder):
    product: Event

    def __init__(self,
                 start_conditions: List[Condition],
                 name: str = "",
                 priority: Priority = Priority.PARALLEL,
                 maximum_execution_count: int = 1):
        self.maximum_execution_count = maximum_execution_count
        self.name = name
        self.priority = priority
        self.trigger_builder = StartTriggerBuilder()
        self.trigger_builder.make_condition_group(start_conditions)
        self.start_trigger = self.trigger_builder.get_result()
        self.actions = []
        self.action_builder = ActionBuilder()

    def add_global_action(self, name: str, global_action: GlobalAction):
        self.action_builder.make_action(name=name, global_action=global_action)

        self.actions.append(self.action_builder.get_result())

    def add_user_defined_action(self, name: str,
                                user_defined_action: UserDefinedAction):
        self.action_builder.make_action(
            name=name, user_defined_action=user_defined_action)
        self.actions.append(self.action_builder.get_result())

    def add_private_action(self, name: str, private_action: PrivateAction):
        self.action_builder.make_action(name=name,
                                        private_action=private_action)
        self.actions.append(self.action_builder.get_result())

    def update_actions(self, actions: List[Action]):
        self.actions = actions

    def get_result(self) -> Event:
        assert len(self.actions) > 1, "Actions should not be empty"

        self.product = Event(
            maximumExecutionCount=self.maximum_execution_count,
            name=self.name,
            startTrigger=self.start_trigger,
            actions=self.actions)
        return self.product
