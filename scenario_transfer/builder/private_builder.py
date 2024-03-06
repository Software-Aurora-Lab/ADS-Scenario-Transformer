from typing import List, Optional
from openscenario_msgs import Private, PrivateAction, Waypoint, ScenarioObject, RoutingAction, AssignRouteAction, AcquirePositionAction, Route, TeleportAction, EntityRef, Entity
from scenario_transfer.builder import Builder


class PrivateBuilder(Builder):
    waypoints: List[Waypoint]
    scenario_object: ScenarioObject
    teleport_action: TeleportAction
    routing_action: RoutingAction

    product: Private

    def __init__(self, waypoints: List[Waypoint]):
        self.waypoints = waypoints

    def make_entity(self, scenario_object: ScenarioObject):
        self.scenario_object = scenario_object

    def make_teleport_action(self):
        self.teleport_action = TeleportAction(
            position=self.waypoints[0].position)

    def make_routing_action(self):
        if len(self.waypoints) > 3:
            self.routing_action = RoutingAction(
                assignRouteAction=AssignRouteAction(
                    route=Route(closed=False,
                                name="ego route",
                                parameterDeclarations=[],
                                waypoints=self.waypoints[1:])))
        else:
            self.routing_action = RoutingAction(
                acquirePositionAction=AcquirePositionAction(
                    position=self.waypoints[-1].position))

    def update_route_name(self, name: str):
        if not self.routing_action.assignRouteAction:
            return

        self.routing_action.assignRouteAction.route.name = name

    def get_result(self) -> Private:
        return Private(entityRef=self.scenario_object.name,
                       privateActions=[
                           PrivateAction(teleportAction=self.teleport_action),
                           PrivateAction(routingAction=self.routing_action)
                       ])
