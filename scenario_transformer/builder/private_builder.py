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

    def make_routing_action_with_teleport_action(self, waypoints: List[Waypoint], closed: bool, name: str):
        assert len(waypoints) > 1, "The number of waypoints should be larger than 2"

        self.make_teleport_action(position= waypoints[0].position)
        
        routing_action_builder = RoutingActionBuilder()
        if len(waypoints) > 3:
            routing_action_builder.make_assign_route_action(
                closed=closed,
                name=name,
                parameter_declarations=[],
                waypoints=waypoints[1:])
        else:
            if waypoints[-1].position.lanePosition:
                routing_action_builder.make_acquire_position_action(lane_position=waypoints[-1].position.lanePosition)
            else:
                routing_action_builder.make_acquire_position_action(world_position=waypoints[-1].position.worldPosition)

        routing_action = routing_action_builder.get_result()
        private_action_builder = PrivateActionBuilder()
        private_action_builder.make_routing_action(routing_action=routing_action)
        self.private_actions.append(private_action_builder.get_result())
        

    def get_result(self) -> Private:
        self.product = Private(entityRef=self.scenario_object.name,
                               privateActions=self.private_actions)
        return self.product
