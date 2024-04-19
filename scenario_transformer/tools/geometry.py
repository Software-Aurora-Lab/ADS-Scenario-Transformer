from typing import Optional
import math
import lanelet2
from lanelet2.projection import MGRSProjector
from lanelet2.core import (Lanelet, LaneletMap, GPSPoint, BasicPoint2d,
                           BasicPoint3d, getId, Point3d)
from lanelet2.io import Origin
from lanelet2.geometry import (findNearest, distanceToCenterline2d, distance,
                               findWithin3d, findWithin2d,
                               approximatedLength2d, inside, length2d, project)
from pyproj import Proj, transform
from modules.common.proto.geometry_pb2 import PointENU
from openscenario_msgs import LanePosition, WorldPosition, Orientation, ReferenceContext


class Geometry:

    @staticmethod
    def find_lanelet(map: LaneletMap,
                     basic_point: BasicPoint3d) -> Optional[Lanelet]:
        found_lanes = findWithin3d(map.laneletLayer, basic_point, 0)
        return found_lanes[0][1] if found_lanes else None

    @staticmethod
    def lane_position(lanelet: Lanelet,
                      basic_point: BasicPoint3d,
                      heading=0.0) -> Optional[LanePosition]:
        point3d = Point3d(getId(), basic_point.x, basic_point.y, basic_point.z)
        basic_point2d = BasicPoint2d(basic_point.x, basic_point.y)

        if not inside(lanelet, basic_point2d):
            return None

        max_centerline_length = math.floor(length2d(lanelet))
        
        # Calculation of s attribute is simplified.
        # https://releases.asam.net/OpenDRIVE/1.6.0/ASAM_OpenDRIVE_BS_V1-6-0.html#_reference_line_coordinate_systems
        s_attribute = min(max_centerline_length, distance(lanelet.centerline[0], point3d))
        t_attribute = distanceToCenterline2d(lanelet, basic_point2d)

        return LanePosition(
            roadId='',
            laneId=str(lanelet.id),
            s=s_attribute,
            offset=t_attribute,
            orientation=Orientation(
                h=heading,
                p=0,
                r=0,
                type=ReferenceContext.REFERENCECONTEXT_RELATIVE))

    @staticmethod
    def utm_to_WGS(pose: PointENU, zone=10) -> GPSPoint:
        utm_proj = Proj(proj="utm", zone=zone, ellps="WGS84")
        lon, lat = utm_proj(pose.x, pose.y, inverse=True)
        return GPSPoint(lat=lat, lon=lon, ele=0)

    @staticmethod
    def project_UTM_to_lanelet(projector: MGRSProjector,
                               pose: PointENU) -> BasicPoint3d:
        gps_point = Geometry.utm_to_WGS(pose)
        return projector.forward(gps_point)
