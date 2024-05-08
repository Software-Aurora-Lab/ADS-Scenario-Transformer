from modules.common.proto.geometry_pb2 import PointENU
from modules.routing.proto.routing_pb2 import LaneWaypoint
from ads_scenario_transformer.transformer import LaneWaypointTransformer
from ads_scenario_transformer.transformer.lane_waypoint_transformer import LaneWaypointTransformerConfiguration


def test_utm_type_lane_waypoint_transformer(vector_map_parser,
                                            apollo_map_parser, entities,
                                            localization_poses):

    point = localization_poses[56].pose.position
    pose = PointENU(x=point.x, y=point.y, z=point.z)
    lane_waypoint = LaneWaypoint(pose=pose)

    transformer = LaneWaypointTransformer(
        configuration=LaneWaypointTransformerConfiguration(
            vector_map_parser=vector_map_parser,
            scenario_object=entities.scenarioObjects[0],
            apollo_map_parser=apollo_map_parser,
            reference_points=[
                localization_poses[0].pose.position,
                localization_poses[-1].pose.position
            ]))

    openscenario_waypoint = transformer.transform(source=lane_waypoint)

    lane_position = openscenario_waypoint.position.lanePosition

    assert lane_position.laneId == "15"
    assert lane_position.offset == -0.21234711002946863
    assert lane_position.s == 44.94214913248086
    assert lane_position.orientation.h == 0
