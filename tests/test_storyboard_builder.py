import pytest
import yaml
from openscenario_msgs import Actors, Event, Entities, Priority, ManeuverGroup, Story, Act, Storyboard, Init
from scenario_transformer.builder.storyboard.actors_builder import ActorsBuilder
from scenario_transformer.builder.storyboard.event_builder import EventBuilder
from scenario_transformer.builder.storyboard.condition_builder import ConditionBuilder
from scenario_transformer.builder.storyboard.story_builder import StoryBuilder
from scenario_transformer.builder.storyboard.act_builder import ActBuilder
from scenario_transformer.builder.storyboard.maneuver_group_builder import ManeuverGroupBuilder
from scenario_transformer.builder.storyboard.maneuver_builder import ManeuverBuilder
from scenario_transformer.builder.storyboard.init_builder import InitBuilder
from scenario_transformer.builder.storyboard.storyboard_builder import StoryboardBuilder


def test_actors_builder(entities):
    builder = ActorsBuilder(entities=entities, scenario_object_name="ego")
    actors = builder.get_result()

    assert isinstance(actors, Actors)
    assert actors.selectTriggeringEntities == False
    assert actors.entityRefs[0].entityRef == "ego"


def test_event_builder(by_entity_collision_condition,
                       by_value_traffic_condition, private_action,
                       global_action):
    condition_builder = ConditionBuilder()
    condition_builder.make_by_entity_condition(by_entity_collision_condition)

    condition1 = condition_builder.get_result()

    condition_builder.make_by_value_condition(by_value_traffic_condition)
    condition2 = condition_builder.get_result()

    builder = EventBuilder(start_conditions=[condition1, condition2],
                           name="test event",
                           priority=Priority.PARALLEL,
                           maximum_execution_count=1)

    builder.add_global_action(name="GlobalAction", global_action=global_action)
    builder.add_private_action(name="PrivateAction",
                               private_action=private_action)

    event = builder.get_result()
    assert isinstance(event, Event)
    assert event.name == "test event"
    event.actions[-1].privateAction.teleportAction

    lane_position_in_teleport_action = event.actions[
        -1].privateAction.teleportAction.position.lanePosition

    assert lane_position_in_teleport_action.laneId == "154"
    assert lane_position_in_teleport_action.s == 10.9835
    assert lane_position_in_teleport_action.offset == -0.5042

    collision_wrapper_condition = event.startTrigger.conditionGroups[
        0].conditions[0]

    by_entity_condition = collision_wrapper_condition.byEntityCondition
    assert by_entity_condition is not None
    assert by_entity_condition.triggeringEntities.entityRefs[
        0].entityRef == "ego"
    assert by_entity_condition.entityCondition.collisionCondition is not None
    assert by_entity_condition.entityCondition.collisionCondition.entityRef.entityRef == "npc_1"


def test_maneuver_group_builder(actors, maneuvers):
    assert len(maneuvers) == 2

    builder = ManeuverGroupBuilder()
    builder.make_maneuvers(maneuvers=maneuvers)
    builder.make_actors(actors=actors)
    maneuver_group = builder.get_result()
    assert isinstance(maneuver_group, ManeuverGroup)

    maneuver = maneuver_group.maneuvers[0]
    assert maneuver.events[0].name == "speed_check"
    assert maneuver.events[0].actions[
        0].userDefinedAction.customCommandAction.type == ":"
    assert maneuver.events[-1].startTrigger.conditionGroups[0].conditions[
        0].byValueCondition.simulationTimeCondition.value == 0.0


def test_maneuver_builder(events):
    builder = ManeuverBuilder(name="test maneuver")
    builder.make_events(events=events)
    maneuver = builder.get_result()
    assert len(maneuver.events) == 3
    assert maneuver.events[0].name == "speed_check"
    assert maneuver.events[0].actions[
        0].userDefinedAction.customCommandAction.type == ":"
    assert maneuver.events[-1].startTrigger.conditionGroups[0].conditions[
        0].byValueCondition.simulationTimeCondition.value == 180.0


def test_act_builder(maneuver_groups, start_trigger):
    builder = ActBuilder()
    builder.make_maneuver_groups(maneuver_groups=maneuver_groups)
    builder.make_start_trigger(trigger=start_trigger)
    act = builder.get_result()

    assert isinstance(act, Act)

    maneuver = act.maneuverGroups[0].maneuvers[0]
    assert maneuver.events[0].name == "speed_check"
    assert maneuver.events[0].actions[
        0].userDefinedAction.customCommandAction.type == ":"
    assert maneuver.events[-1].startTrigger.conditionGroups[0].conditions[
        0].byValueCondition.simulationTimeCondition.value == 0.0


def test_story_builder(acts):
    builder = StoryBuilder()
    builder.make_acts(acts=acts)
    story = builder.get_result()

    assert isinstance(story, Story)

    maneuver = story.acts[0].maneuverGroups[0].maneuvers[0]
    assert maneuver.events[0].name == "speed_check"
    assert maneuver.events[0].actions[
        0].userDefinedAction.customCommandAction.type == ":"
    assert maneuver.events[-1].startTrigger.conditionGroups[0].conditions[
        0].byValueCondition.simulationTimeCondition.value == 0.0


def test_init_builder(init_actions):
    builder = InitBuilder()

    builder.make_global_actions(global_actions=init_actions.globalActions)
    builder.make_user_defined_actions(
        user_defined_actions=init_actions.userDefinedActions)
    builder.make_privates(privates=init_actions.privates)
    init = builder.get_result()

    assert isinstance(init, Init)
    assert len(init.actions.privates) == 3


def test_storyboard_builder(storyboard, story, stop_trigger):
    builder = StoryboardBuilder()

    builder.make_init(init=storyboard.init)
    builder.make_stories(stories=[story])
    builder.make_stop_trigger(trigger=stop_trigger)

    storyboard = builder.get_result()
    assert isinstance(storyboard, Storyboard)
