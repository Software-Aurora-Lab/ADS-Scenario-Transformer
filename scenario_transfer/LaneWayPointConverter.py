# import lanelet2

from apollo_msgs import PointENU
from openscenario_msgs import (LanePosition)

from Geometry import Geometry
from LaneWayPoint import LaneWaypoint

class LaneWayPointConverter:
    @staticmethod
    def project_lanewaypoint_to_laneposition(lanelet: Lanelet, waypoint: LaneWayPoint) -> LanePosition:

        if waypoint.pose:
            pose = PointENU(x=waypoint.pose.x, y=waypoint.pose.y, z=0)
            projected_point = Geometry.project_UTM_to_lanelet(projector=lanelet.projector, pose=pose)
            return Geometry.lane_position(lanelet=lanelet, basic_point=projected_point)