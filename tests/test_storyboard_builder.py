import unittest
import yaml
from openscenario_msgs import Actors
from scenario_transfer.builder.story_board.actors_builder import ActorsBuilder
from scenario_transfer.builder.entities_builder import EntityType, EntitiesBuilder


class TestBuilder(unittest.TestCase):

    def setUp(self):
        input_dir = "./tests/data/"
        self.route_file_path = input_dir + "openscenario_route.yaml"
        builder = EntitiesBuilder(entities=[
            EntityType.NPC, EntityType.NPC, EntityType.EGO,
            EntityType.PEDESTRIAN, EntityType.NPC
        ])
        self.entities = builder.get_result()

    def test_actors_builder(self):

        builder = ActorsBuilder(entities=self.entities)
        builder.set_key(name_key="ego")
        actors = builder.get_result()

        self.assertIsInstance(actors, Actors)
        self.assertEqual(actors.selectTriggeringEntities, False)
        self.assertEqual(actors.entityRef[0], "ego")
