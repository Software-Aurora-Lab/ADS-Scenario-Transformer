import unittest
import lanelet2
from lanelet2.projection import MGRSProjector
from lanelet2.io import Origin
from modules.common.proto.geometry_pb2 import PointENU
from modules.routing.proto.routing_pb2 import LaneWaypoint
from openscenario_msgs import Waypoint, LanePosition
from scenario_transfer.transformer import LaneWaypointTransformer
from scenario_transfer.transformer.lane_waypoint_transformer import LaneWaypointTransformerConfiguration

def test_utm_type_lane_waypoint_transformer(lanelet_map, mgrs_projector):
    point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)

    lane_waypoint = LaneWaypoint(pose=point)

    transformer = LaneWaypointTransformer(configuration=LaneWaypointTransformerConfiguration(
        lanelet_map=lanelet_map, 
        projector=mgrs_projector)
    )

    openscenario_waypoint = transformer.transform(source=lane_waypoint)

    lane_position = openscenario_waypoint.position.lanePosition
    
    assert lane_position.laneId == "22"
    assert lane_position.offset == 0.1750399287494411
    assert lane_position.s == 35.714714923990464
    assert lane_position.orientation.h == 0


def test_laneId_type_lane_waypoint_transformer(lanelet_map, mgrs_projector, apollo_map_parser):
    lane_waypoint = LaneWaypoint(id="lane_26", s=26.2)
    
    transformer = LaneWaypointTransformer(configuration=LaneWaypointTransformerConfiguration(
        lanelet_map=lanelet_map, 
        projector=mgrs_projector,
        apollo_map_parser=apollo_map_parser)
    )
    
    openscenario_waypoint = transformer.transform(source=lane_waypoint)
    
    lane_position = openscenario_waypoint.position.lanePosition

    assert lane_position.laneId == "149"
    assert lane_position.offset == 1.4604610803960605
    assert lane_position.s == 26.739416492972932
    assert lane_position.orientation.h == -1.9883158777364047