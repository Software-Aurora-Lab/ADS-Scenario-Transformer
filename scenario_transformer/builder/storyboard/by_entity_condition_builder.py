from typing import Optional
from openscenario_msgs import TriggeringEntities, Position, RelativeDistanceType, DirectionalDimension, CoordinateSystem, RoutingAlgorithm
import openscenario_msgs.common_pb2 as common_pb2
from openscenario_msgs.common_pb2 import ByEntityCondition, EntityCondition, EndOfRoadCondition, CollisionCondition, OffroadCondition, TimeHeadwayCondition, TimeToCollisionCondition, AccelerationCondition, StandStillCondition, SpeedCondition, RelativeSpeedCondition, TraveledDistanceCondition, ReachPositionCondition, DistanceCondition, RelativeDistanceCondition, RelativeClearanceCondition
from scenario_transformer.builder import Builder
from openscenario_msgs import Rule, EntityRef


class ByEntityConditionBuilder(Builder):
    product: ByEntityCondition
    entity_condition: EntityCondition
    triggering_entities: TriggeringEntities

    def __init__(self, triggering_entity: str):

        self.triggering_entities = TriggeringEntities(
            triggeringEntitiesRule=common_pb2.TriggeringEntities.
            TriggeringEntitiesRule.ANY,
            entityRefs=[EntityRef(entityRef=triggering_entity)
                        ])  # limit to use single entity

    def make_collision_condition(self, colliding_entity_name: str):
        condition = CollisionCondition(entityRef=EntityRef(
            entityRef=colliding_entity_name))
        self.entity_condition = EntityCondition(collisionCondition=condition)

    def make_time_headway_condition(self, coordinateSystem: CoordinateSystem,
                                    entity_name: str,
                                    relativeDistanceType: RelativeDistanceType,
                                    rule: Rule, value_in_sec: float):
        condition = TimeHeadwayCondition(
            coordinateSystem=coordinateSystem,
            entityRef=entity_name,
            freespace=False,
            relativeDistanceType=relativeDistanceType,
            rule=rule,
            value=value_in_sec)
        self.entity_condition = EntityCondition(timeHeadwayCondition=condition)

    def make_acceleration_condition(self, value_in_ms: float, rule: Rule):
        condition = AccelerationCondition(value=value_in_ms, rule=rule)
        self.entity_condition = EntityCondition(
            accelerationCondition=condition)

    def make_stand_still_condition(self, duration_in_sec: float):
        condition = StandStillCondition(duration=duration_in_sec)
        self.entity_condition = EntityCondition(standStillCondition=condition)

    def make_speed_condition(self,
                             value_in_ms: float,
                             rule: Rule,
                             direction: DirectionalDimension = None):
        condition = SpeedCondition(direction=direction,
                                   rule=rule,
                                   value=value_in_ms)
        self.entity_condition = EntityCondition(speedCondition=condition)

    def make_reach_position_condition(self, tolerance: float,
                                      position: Position):
        assert position.worldPosition is not None or position.lanePosition is not None

        condition = ReachPositionCondition(tolerance=tolerance,
                                           position=position)
        self.entity_condition = EntityCondition(
            reachPositionCondition=condition)

    def make_distance_condition(
            self,
            freespace: bool,
            value_in_meter: float,
            rule: Rule,
            position: Position,
            coordinateSystem: CoordinateSystem = None,
            relativeDistanceType: RelativeDistanceType = None,
            routingAlgorithm: RoutingAlgorithm = None):
        assert position.worldPosition is not None or position.lanePosition is not None

        condition = DistanceCondition(
            coordinateSystem=coordinateSystem,
            freespace=freespace,
            relativeDistanceType=relativeDistanceType,
            routingAlgorithm=routingAlgorithm,
            rule=rule,
            value=value_in_meter,
            position=position)
        self.entity_condition = EntityCondition(distanceCondition=condition)

    def make_relative_distance_condition(
            self, entity_name: str, relativeDistanceType: RelativeDistanceType,
            value_in_meter: float, freespace: bool, rule: Rule):
        condition = RelativeDistanceCondition(
            entityRef=entity_name,
            relativeDistanceType=relativeDistanceType,
            value=value_in_meter,
            freespace=freespace,
            rule=rule)
        self.entity_condition = EntityCondition(
            relativeDistanceCondition=condition)

    def get_result(self) -> ByEntityCondition:
        assert self.entity_condition is not None
        assert self.triggering_entities is not None

        self.product = ByEntityCondition(
            triggeringEntities=self.triggering_entities,
            entityCondition=self.entity_condition)
        return self.product

    # UnSpecified

    def make_relative_clearance_condition(self):
        raise TypeError(
            f"Unspecified type: {type(RelativeClearanceCondition()).__name__}")

    # Unsupported condition types

    def make_end_of_road_condition(self):
        raise TypeError(
            f"Unsupported type: {type(EndOfRoadCondition()).__name__}")

    def make_offroad_condition(self):
        raise TypeError(
            f"Unsupported type: {type(OffroadCondition()).__name__}")

    def make_time_to_collision_condition(self):
        raise TypeError(
            f"Unsupported type: {type(TimeToCollisionCondition()).__name__}")

    def make_relative_speed_condition(self):
        raise TypeError(
            f"Unsupported type: {type(RelativeSpeedCondition()).__name__}")

    def make_traveled_distance_condition(self):
        raise TypeError(
            f"Unsupported type: {type(TraveledDistanceCondition()).__name__}")
