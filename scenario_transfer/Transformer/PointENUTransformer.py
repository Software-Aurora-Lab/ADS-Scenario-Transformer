from typing import Type, TypeVar, List

from lanelet2.core import GPSPoint, LaneletMap

from apollo_msgs import PointENU
from openscenario_msgs import LanePosition

from scenario_transfer import (Transformable, Geometry, TransformRuleContainer)

# properties = [lanelet2.core.LaneletMap]
class PointENUTransformer(Transformable):
    T = PointENU
    V = GPSPoint
    X = LanePosition

    def __init__(self, properties: List):
        self.properties = properties

    def transform1(self, source: T) -> V:
        pose = Geometry.utm_to_WGS(pose= source)

        assert(self.V in TransformRuleContainer.rules[type(pose)])
        return pose
    
    def transform2(self, source: T) -> X:
        lanelet_map = self.properties[0]
        
        pose = self.transform1(source=source)
        projected_point = Geometry.project_UTM_to_lanelet(projector=lanelet_map.projector, pose=pose)
        lanelet = Geometry.find_lanelet(lanelet_map, projected_point)
        lane_position = Geometry.lane_position(lanelet=lanelet, basic_point= projected_point)

        assert(self.X in TransformRuleContainer.rules[type(pose)])
        return lane_position