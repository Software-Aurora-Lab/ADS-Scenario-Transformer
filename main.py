import lanelet2
from lanelet2.projection import (LocalCartesianProjector, UtmProjector)
from lanelet2.core import (GPSPoint, BasicPoint2d, BasicPoint3d, getId, Point2d, Point3d)
from lanelet2.io import Origin
from lanelet2.geometry import (findNearest, distanceToCenterline2d, distanceToCenterline3d, distance, inside, findWithin3d)
from pprint import pprint

origin = Origin(37.04622247590861, -123.00000000000001, 0)
map = lanelet2.io.load("./map/BorregasAve/lanelet2_map.osm", UtmProjector(origin))

routingPoints = [BasicPoint3d(86973.4293, 41269.817, -5.6269),
                BasicPoint3d(86993.2289, 41343.5182, -4.5032),
                BasicPoint3d(87014.2461, 41427.1901, -3.2535)]

def prop(obj):
    return str(type(obj)) + ' ' + str(list(filter(lambda name: not name.startswith('__'), dir(obj))))

def findLanelet(map, routingPoint: BasicPoint3d) -> lanelet2.core.Lanelet:
    found_lane = findWithin3d(map.laneletLayer, routingPoint, 0)[0]

    if found_lane:
        return found_lane[1]

    routingPoint2d = BasicPoint2d(routingPoint.x, routingPoint.y)
    return findNearest(map.laneletLayer, routingPoint2d, 1)[0][1]

for idx, routingPoint in enumerate(routingPoints):
    lanelet = findLanelet(map=map, routingPoint=routingPoint)
    if lanelet is None:
        continue

    print(lanelet)
    laneId = lanelet.id
    point3d = Point3d(getId(), routingPoint.x, routingPoint.y, routingPoint.z)
    s_attribute = distance(lanelet.leftBound[0], point3d) # Tier4 Scenario editor uses first element of the left bound
    print("LaneID", laneId)
    print("s_attribute", s_attribute)

    routingPoint2d = BasicPoint2d(routingPoint.x, routingPoint.y)
    tAttr = distanceToCenterline2d(lanelet, routingPoint2d)
    print("centerline", prop(lanelet.centerline))
    print("t_attribute", tAttr)
