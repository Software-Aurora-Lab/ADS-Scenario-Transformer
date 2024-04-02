import pytest
import yaml
from openscenario_msgs import Actors, Event, Entities, Priority, Position, LanePosition, PrivateAction, GlobalAction
from scenario_transfer.builder.story_board.actors_builder import ActorsBuilder
from scenario_transfer.builder.story_board.event_builder import EventBuilder
from scenario_transfer.builder.story_board.private_action_builder import PrivateActionBuilder
from scenario_transfer.builder.story_board.global_action_builder import GlobalActionBuilder
from scenario_transfer.builder.entities_builder import EntityType, EntitiesBuilder


def test_actors_builder(entities):
    builder = ActorsBuilder(entities=entities)
    builder.set_key(name_key="ego")
    actors = builder.get_result()

    assert isinstance(actors, Actors)
    assert actors.selectTriggeringEntities == False
    assert actors.entityRef[0] == "ego"


def test_event_builder(private_action, global_action):
    builder = EventBuilder(start_conditions=[],
                           name="test event",
                           priority=Priority.PARALLEL,
                           maximum_execution_count=1)

    builder.add_global_action(name="GlobalAction", global_action=global_action)
    builder.add_private_action(name="PrivateAction",
                               private_action=private_action)

    event = builder.get_result()
    assert isinstance(event, Event)
