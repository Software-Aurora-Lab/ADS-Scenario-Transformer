import pytest
from openscenario_msgs import GlobalAction, Entities, Position, LanePosition
from scenario_transfer.builder.story_board.global_action_builder import GlobalActionBuilder
from scenario_transfer.builder.entities_builder import EntityType, EntitiesBuilder


@pytest.fixture
def entities() -> Entities:
    builder = EntitiesBuilder(entities=[
        EntityType.NPC, EntityType.NPC, EntityType.EGO, EntityType.PEDESTRIAN,
        EntityType.NPC
    ])
    return builder.get_result()


@pytest.fixture
def ego_name(entities) -> str:
    return entities.scenarioObjects[0].name


def test_global_action_builder_add_entity_action(ego_name):
    assert ego_name == "ego"
    builder = GlobalActionBuilder()

    position = Position(
        lanePosition=LanePosition(laneId="154", s=10.9835, offset=-0.5042))

    builder.make_add_entity_action(position=position, entity_name=ego_name)
    action = builder.get_result()

    assert isinstance(action, GlobalAction)
    assert action.entityAction.entityRef == ego_name
    assert action.entityAction.addEntityAction.position.lanePosition.laneId == "154"


def test_global_action_builder_delete_entity_action(ego_name):
    assert ego_name == "ego"
    builder = GlobalActionBuilder()
    builder.make_delete_entity_action(entity_name=ego_name)
    action = builder.get_result()

    assert isinstance(action, GlobalAction)
    assert action.entityAction.entityRef == ego_name
    assert action.entityAction.deleteEntityAction is not None
