from modules.common.proto.geometry_pb2 import PointENU
from modules.routing.proto.routing_pb2 import LaneWaypoint
from ads_scenario_transformer.transformer import LaneWaypointTransformer
from ads_scenario_transformer.transformer.lane_waypoint_transformer import LaneWaypointTransformerConfiguration
from ads_scenario_transformer.builder.entities_builder import ASTEntityType


def test_utm_type_lane_waypoint_transformer(lanelet_map, mgrs_projector,
                                            entities):
    point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)

    lane_waypoint = LaneWaypoint(pose=point)

    transformer = LaneWaypointTransformer(
        configuration=LaneWaypointTransformerConfiguration(
            lanelet_map=lanelet_map,
            projector=mgrs_projector,
            lanelet_subtypes=ASTEntityType.EGO.available_lanelet_subtype(),
            scenario_object=entities.scenarioObjects[0]))

    openscenario_waypoint = transformer.transform(source=lane_waypoint)

    lane_position = openscenario_waypoint.position.lanePosition

    assert lane_position.laneId == "22"
    assert lane_position.offset == 0.2289137647592503
    assert lane_position.s == 35.812947374714085
    assert lane_position.orientation.h == 0


def test_laneId_type_lane_waypoint_transformer(lanelet_map, mgrs_projector,
                                               apollo_map_parser, entities):
    lane_waypoint = LaneWaypoint(id="lane_26", s=26.2)

    transformer = LaneWaypointTransformer(
        configuration=LaneWaypointTransformerConfiguration(
            lanelet_map=lanelet_map,
            projector=mgrs_projector,
            apollo_map_parser=apollo_map_parser,
            lanelet_subtypes=ASTEntityType.EGO.available_lanelet_subtype(),
            scenario_object=entities.scenarioObjects[0]))

    openscenario_waypoint = transformer.transform(source=lane_waypoint)

    lane_position = openscenario_waypoint.position.lanePosition

    assert lane_position.laneId == "149"
    assert lane_position.offset == 0.9375
    assert lane_position.s == 26.739416492972932
    assert lane_position.orientation.h == 0.0
