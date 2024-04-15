from typing import List
from openscenario_msgs import Event, Action, Condition, Priority, GlobalAction, UserDefinedAction, PrivateAction, Rule, Position
from scenario_transformer.builder import Builder
from scenario_transformer.builder.storyboard.action_builder import ActionBuilder
from scenario_transformer.builder.storyboard.trigger_builder import StartTriggerBuilder
from scenario_transformer.builder.storyboard.condition_builder import ConditionBuilder
from scenario_transformer.builder.storyboard.by_entity_condition_builder import ByEntityConditionBuilder
from scenario_transformer.builder.storyboard.user_defined_action_builder import UserDefinedActionBuilder, BuiltInUserDefinedActionType


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
        assert len(self.actions) > 0, "Actions should not be empty"

        self.product = Event(
            maximumExecutionCount=self.maximum_execution_count,
            name=self.name,
            startTrigger=self.start_trigger,
            actions=self.actions)
        return self.product

    @staticmethod
    def exit_failure_event(rule: Rule, value_in_sec: float) -> Event:
        exit_failure_condtion = ConditionBuilder.simulation_time_condition(
            rule=Rule.GREATER_THAN, value_in_sec=180)

        event_builder = EventBuilder(start_conditions=[exit_failure_condtion])

        exit_failure_action = UserDefinedActionBuilder.built_in_action(
            type=BuiltInUserDefinedActionType.EXIT_FAILURE)
        event_builder.add_user_defined_action(
            name="exit_failure", user_defined_action=exit_failure_action)
        return event_builder.get_result()

    @staticmethod
    def exit_success_event(ego_name: str, ego_end_position: Position) -> Event:

        by_entity_condition_builder = ByEntityConditionBuilder(
            triggering_entity=ego_name)
        by_entity_condition_builder.make_reach_position_condition(
            position=ego_end_position, tolerance=1)

        condition_builder = ConditionBuilder()
        condition_builder.make_by_entity_condition(
            by_entity_condition=by_entity_condition_builder.get_result())
        exit_success_condition = condition_builder.get_result()
        exit_success_action = UserDefinedActionBuilder.built_in_action(
            type=BuiltInUserDefinedActionType.EXIT_SUCCESS)

        event_builder = EventBuilder(start_conditions=[exit_success_condition])
        event_builder.add_user_defined_action(
            name="exit_success", user_defined_action=exit_success_action)
        return event_builder.get_result()
