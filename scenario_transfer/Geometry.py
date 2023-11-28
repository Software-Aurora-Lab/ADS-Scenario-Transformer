from typing import Optional

import lanelet2
from lanelet2.projection import UtmProjector
from lanelet2.core import (Lanelet, LaneletMap, GPSPoint, BasicPoint2d, BasicPoint3d, getId, Point2d, Point3d)
from lanelet2.io import Origin
from lanelet2.geometry import (findNearest, distanceToCenterline2d, distance, findWithin3d)
from pyproj import Proj, transform

from apollo_msgs import PointENU
from openscenario_msgs import LanePosition

class Geometry:
    @staticmethod
    def find_lanelet(map: LaneletMap, basic_point: BasicPoint3d) -> Optional[Lanelet]:
        found_lane = findWithin3d(map.laneletLayer, basic_point, 0)[0]

        if found_lane:
            return found_lane[1]

        basic_point2d = BasicPoint2d(basic_point.x, basic_point.y)
        return findNearest(map.laneletLayer, basic_point2d, 1)[0][1]

    @staticmethod
    def lane_position(lanelet: Lanelet, basic_point: BasicPoint3d) -> LanePosition:
        point3d = Point3d(getId(), basic_point.x, basic_point.y, basic_point.z)
        s_attribute = distance(lanelet.leftBound[0], point3d)

        basic_point2d = BasicPoint2d(basic_point.x, basic_point.y)
        t_attribute = distanceToCenterline2d(lanelet, basic_point2d)

        return LanePosition(laneId=lanelet.id, s=s_attribute, offset=t_attribute)
    
    @staticmethod
    def utm_to_WGS(pose: PointENU) -> GPSPoint:
        utm_proj = Proj(proj="utm", zone=pose.zone, ellps="WGS84")
        lon, lat = utm_proj(pose.x, pose.y, inverse=True)
        return GPSPoint(lat=lat, lon=lon, ele=0)

    @staticmethod
    def project_UTM_to_lanelet(projector: UtmProjector, pose: PointENU):
        gps_point = Geometry.utm_to_WGS(pose)
        return projector.forward(gps_point)