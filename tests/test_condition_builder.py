import unittest
import yaml
from openscenario_msgs import Actors, Condition, ByEntityCondition, Rule
from scenario_transfer.builder.entities_builder import EntityType, EntitiesBuilder
from scenario_transfer.builder.story_board.by_entity_condition_builder import ByEntityConditionBuilder


class TestBuilder(unittest.TestCase):

    def setUp(self):
        input_dir = "./tests/data/"
        self.route_file_path = input_dir + "openscenario_route.yaml"
        builder = EntitiesBuilder(entities=[
            EntityType.NPC, EntityType.NPC, EntityType.EGO,
            EntityType.PEDESTRIAN, EntityType.NPC
        ])
        self.entities = builder.get_result()

    def test_entity_condition_builder_collision(self):

        ego_name = self.entities.scenarioObjects[0].name
        colliding_npc_name = self.entities.scenarioObjects[1].name

        builder = ByEntityConditionBuilder(triggering_entity=ego_name)
        builder.make_collision_condition(
            colliding_entity_name=colliding_npc_name)
        by_entity_condition = builder.get_result()

        assert by_entity_condition is not None
        assert by_entity_condition.triggeringEntities.entityRef[
            0].entityRef == "ego"
        assert by_entity_condition.entityCondition.collisionCondition is not None
        assert by_entity_condition.entityCondition.collisionCondition.entityRef.entityRef == "npc_1"

    def test_entity_condition_builder_acceleration(self):

        ego_name = self.entities.scenarioObjects[0].name

        builder = ByEntityConditionBuilder(triggering_entity=ego_name)
        builder.make_acceleration_condition(value_in_ms=10,
                                            rule=Rule.GREATER_THAN)
        by_entity_condition = builder.get_result()

        assert by_entity_condition is not None
        assert by_entity_condition.triggeringEntities.entityRef[
            0].entityRef == "ego"
        assert by_entity_condition.entityCondition.accelerationCondition.value == 10.0
        assert by_entity_condition.entityCondition.accelerationCondition.rule == Rule.GREATER_THAN

    def test_entity_condition_builder_speed(self):

        ego_name = self.entities.scenarioObjects[0].name

        builder = ByEntityConditionBuilder(triggering_entity=ego_name)
        builder.make_speed_condition(value_in_ms=0.001, rule=Rule.GREATER_THAN)
        by_entity_condition = builder.get_result()

        assert by_entity_condition is not None
        assert by_entity_condition.triggeringEntities.entityRef[
            0].entityRef == "ego"
        assert by_entity_condition.entityCondition.speedCondition.value == 0.001
        assert by_entity_condition.entityCondition.speedCondition.rule == Rule.GREATER_THAN

    # def test_condition_builder(self):
    #     builder = ConditionBuilder()
    #     ego_name = self.entities.scenarioObjects[0].name
    #     builder.make_entity_condition(entity_names=[ego_name])
    #     entity_condition = builder.get_result()

    #     self.assertIsInstance(entity_condition, Condition)
    #     self.assertIsInstance(entity_condition.byEntityCondition,
    #                           ByEntityCondition)
