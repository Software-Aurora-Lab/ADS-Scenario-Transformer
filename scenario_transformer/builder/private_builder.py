from typing import List, Optional
from openscenario_msgs import Private, PrivateAction, Waypoint, ScenarioObject, RoutingAction, AssignRouteAction, AcquirePositionAction, Route, TeleportAction, EntityRef, Entity, Position
from scenario_transformer.builder import Builder
from scenario_transformer.builder.storyboard.private_action_builder import PrivateActionBuilder
from scenario_transformer.builder.storyboard.routing_action_builder import RoutingActionBuilder

class PrivateBuilder(Builder):
    scenario_object: ScenarioObject
    private_actions: List[PrivateAction]
    
    product: Private

    def __init__(self, scenario_object: ScenarioObject):
        self.scenario_object = scenario_object
        self.private_actions = []

    def make_teleport_action(self, position: Position):
        builder = PrivateActionBuilder()
        if position.lanePosition:
            builder.make_teleport_action(lane_position = position.lanePosition)
        else:
            builder.make_teleport_action(lane_position = position.worldPosition)

        self.private_actions.append(builder.get_result())

    def make_routing_action_with_teleport_action(self, waypoints: List[Waypoint], name: str, closed: bool=False):
        assert len(waypoints) > 1, "The number of waypoints should be larger than 2"

        self.make_teleport_action(position= waypoints[0].position)

        positions = [waypoint.position for waypoint in waypoints]
        private_action_builder = PrivateActionBuilder()
        private_action_builder.make_routing_action(positions=positions[1:], name=name, closed=closed)
        
        self.private_actions.append(private_action_builder.get_result())
        

    def get_result(self) -> Private:
        self.product = Private(entityRef=self.scenario_object.name,
                               privateActions=self.private_actions)
        return self.product
