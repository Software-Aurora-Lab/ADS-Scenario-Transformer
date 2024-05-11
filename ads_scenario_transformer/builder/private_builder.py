from typing import List
from openscenario_msgs import Private, PrivateAction, Waypoint, ScenarioObject, Position
from ads_scenario_transformer.builder import Builder
from ads_scenario_transformer.builder.storyboard.private_action_builder import PrivateActionBuilder


class PrivateBuilder(Builder):
    scenario_object: ScenarioObject
    private_actions: List[PrivateAction]

    product: Private

    def __init__(self, scenario_object: ScenarioObject):
        self.scenario_object = scenario_object
        self.private_actions = []

    def make_teleport_action(self, position: Position):
        builder = PrivateActionBuilder()

        if position.HasField("lanePosition"):
            builder.make_teleport_action(lane_position=position.lanePosition)
        else:
            builder.make_teleport_action(world_position=position.worldPosition)

        self.private_actions.append(builder.get_result())

    def make_routing_action_with_waypoints(self,
                                                 waypoints: List[Waypoint],
                                                 name: str,
                                                 closed: bool = False):
        assert len(
            waypoints) > 1, "The number of waypoints should be larger than 2"

        positions = [waypoint.position for waypoint in waypoints]
        return self.make_routing_action_with_positions(positions=positions,
                                                       name=name,
                                                       closed=False)

    def make_routing_action_with_positions(self,
                                           positions: List[Position],
                                           name: str,
                                           closed: bool = False):
        assert len(
            positions) > 1, "The number of positions should be larger than 2"

        self.make_teleport_action(position=positions[0])

        private_action_builder = PrivateActionBuilder()
        private_action_builder.make_routing_action(positions=positions[1:],
                                                   name=name,
                                                   closed=closed)

        self.private_actions.append(private_action_builder.get_result())

    def get_result(self) -> Private:
        self.product = Private(entityRef=self.scenario_object.name,
                               privateActions=self.private_actions)
        return self.product
