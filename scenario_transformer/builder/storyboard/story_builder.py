from typing import List
from openscenario_msgs import Story, Act, ParameterDeclaration, Rule, Entities, RoutingAction
from scenario_transformer.builder import Builder
from scenario_transformer.builder.storyboard.act_builder import ActBuilder
from scenario_transformer.builder.storyboard.maneuver_group_builder import ManeuverGroupBuilder
from scenario_transformer.builder.storyboard.maneuver_builder import ManeuverBuilder
from scenario_transformer.builder.storyboard.event_builder import EventBuilder
from scenario_transformer.builder.storyboard.trigger_builder import StartTriggerBuilder
from scenario_transformer.builder.storyboard.condition_builder import ConditionBuilder
from scenario_transformer.builder.storyboard.actors_builder import ActorsBuilder


class StoryBuilder(Builder):
    product: Story

    def __init__(self,
                 name: str = "",
                 parameter_declarations: List[ParameterDeclaration] = []):
        self.name = name
        self.parameter_declarations = parameter_declarations

    def make_acts(self, acts: List[Act]):
        self.product = Story(name=self.name,
                             parameterDeclarations=self.parameter_declarations,
                             acts=acts)

    def get_result(self) -> Story:
        assert len(self.product.acts) > 0, "Story needs at least one act"

        return self.product

    @staticmethod
    def default_end_story(entities: Entities,
                          routing_action: RoutingAction) -> Story:
        """
        Create a default ending condition story
        - Exit_Failure condition: Simulation time exceeds 180 seconds
        - Exit_Success condition - ego car reaches destination
        """
        ego_end_position = None
        if routing_action.HasField("assignRouteAction"):
            ego_end_position = routing_action.assignRouteAction.route.waypoints[
                -1].position
        else:
            ego_end_position = routing_action.acquirePositionAction.position

        exit_failure_event = EventBuilder.exit_failure_event(
            rule=Rule.GREATER_THAN, value_in_sec=180)

        ego_name = entities.scenarioObjects[0].name
        exit_success_event = EventBuilder.exit_success_event(
            ego_name=ego_name, ego_end_position=ego_end_position)

        maneuver_builder = ManeuverBuilder()
        maneuver_builder.make_events(
            events=[exit_success_event, exit_failure_event])

        actors_builder = ActorsBuilder()
        actors_builder.add_entity_ref(scenario_object_name=ego_name)

        maneuver_group_builder = ManeuverGroupBuilder()
        maneuver_group_builder.make_maneuvers(maneuvers=[maneuver_builder.get_result()])

        maneuver_group_builder.make_actors(actors=actors_builder.get_result())
        maneuver_group = maneuver_group_builder.get_result()

        strat_trigger = StartTriggerBuilder()
        start_condtion = ConditionBuilder.simulation_time_condition(
            rule=Rule.GREATER_THAN, value_in_sec=0)
        strat_trigger.make_condition_group(conditions=[start_condtion])

        act_builder = ActBuilder(name="End Condition")
        act_builder.make_maneuver_groups(maneuver_groups=[maneuver_group])
        act_builder.make_start_trigger(trigger=strat_trigger.get_result())
        act = act_builder.get_result()

        story_builder = StoryBuilder()
        story_builder.make_acts(acts=[act])
        return story_builder.get_result()
