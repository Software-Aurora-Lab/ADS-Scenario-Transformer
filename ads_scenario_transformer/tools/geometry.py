from typing import Optional, Union, Set
import math
from lanelet2.projection import MGRSProjector
from lanelet2.core import Lanelet, LaneletMap, GPSPoint, BasicPoint2d, BasicPoint3d, getId, Point3d, TrafficLight
from lanelet2.geometry import distanceToCenterline2d, distance, findWithin3d, inside, length2d, findNearest, findWithin2d
from pyproj import Proj
from modules.common.proto.geometry_pb2 import PointENU, Point3D
from modules.map.proto.map_signal_pb2 import Signal
from openscenario_msgs import LanePosition, Orientation, ReferenceContext


class Geometry:

    @staticmethod
    def find_nearest_traffic_light(
            map: LaneletMap, signal: Signal,
            projector: MGRSProjector) -> Optional[TrafficLight]:

        candidates = set()
        for point in signal.boundary.point:
            basic_point = Geometry.project_UTM_point_on_lanelet(
                point=point, projector=projector)
            basic_point2d = BasicPoint2d(basic_point.x, basic_point.y)

            nearest_traffic_elements = findNearest(map.regulatoryElementLayer,
                                                   basic_point2d, 10)

            for traffic_element in nearest_traffic_elements:
                if isinstance(traffic_element[1], TrafficLight):
                    candidates.add(traffic_element)

        if not candidates:
            return None

        min_distance, nearest_traffic_light = min(
            (distance, traffic_light)
            for distance, traffic_light in candidates)
        return nearest_traffic_light

    @staticmethod
    def find_lanelet(map: LaneletMap,
                     basic_point: BasicPoint3d,
                     subtypes: Optional[Set[str]] = None) -> Optional[Lanelet]:
        found_lanes = findWithin3d(layer=map.laneletLayer,
                                   geometry=basic_point,
                                   maxDist=1)

        if subtypes:
            for lanelet in found_lanes:
                if "subtype" in lanelet[1].attributes and lanelet[
                        1].attributes["subtype"] in subtypes:
                    return lanelet[1]
        else:
            if found_lanes:
                return found_lanes[0][1]

        basic_point2d = BasicPoint2d(basic_point.x, basic_point.y)
        found_lanes_2d = findNearest(map.laneletLayer, basic_point2d, 10)

        if subtypes:
            for lanelet in found_lanes_2d:
                if "subtype" in lanelet[1].attributes and lanelet[
                        1].attributes["subtype"] in subtypes:
                    return lanelet[1]
        else:
            if found_lanes_2d:
                return found_lanes_2d[0][1]

        return None

    @staticmethod
    def nearest_lane_position(map: LaneletMap,
                              lanelet: Lanelet,
                              basic_point: BasicPoint3d,
                              heading=0.0) -> Optional[LanePosition]:

        basic_point2d = BasicPoint2d(basic_point.x, basic_point.y)
        t_attribute = distanceToCenterline2d(lanelet, basic_point2d)

        if not inside(lanelet, basic_point2d):
            # If the point is not in lanelet, we find nearest one and use it
            nearest_point_in_lanelets = findNearest(map.pointLayer,
                                                    basic_point2d, 1)
            if not nearest_point_in_lanelets:
                return None

            nearest_point = nearest_point_in_lanelets[0][1]

        max_centerline_length = math.floor(length2d(lanelet))
        point3d = Point3d(getId(), basic_point.x, basic_point.y, basic_point.z)
        # Calculation of s attribute is simplified.
        # https://releases.asam.net/OpenDRIVE/1.6.0/ASAM_OpenDRIVE_BS_V1-6-0.html#_reference_line_coordinate_systems
        s_attribute = min(max_centerline_length,
                          distance(lanelet.centerline[0], point3d))

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
    def utm_to_WGS(point: Union[PointENU, Point3D], zone=10) -> GPSPoint:
        utm_proj = Proj(proj="utm", zone=zone, ellps="WGS84")
        lon, lat = utm_proj(point.x, point.y, inverse=True)
        return GPSPoint(lat=lat, lon=lon, ele=point.z)

    @staticmethod
    def project_UTM_point_on_lanelet(point: Union[PointENU, Point3D],
                                     projector: MGRSProjector,
                                     zone: int = 10) -> BasicPoint3d:
        gps_point = Geometry.utm_to_WGS(point, zone=zone)
        return projector.forward(gps_point)
