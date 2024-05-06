import pytest
from lanelet2.core import BasicPoint3d
from modules.common.proto.geometry_pb2 import PointENU
from openscenario_msgs import LanePosition
from ads_scenario_transformer.tools.geometry import Geometry


def test_projection(mgrs_projector):
    poses = [
        PointENU(x=587079.3045861976, y=4141574.299574421, z=0),
        PointENU(x=587044.4300003723, y=4141550.060588833, z=0)
    ]

    expectations = [
        BasicPoint3d(87079.3, 41574.3, 0),
        BasicPoint3d(87044.4, 41550.1, 0)
    ]
    for pose, expectation in zip(poses, expectations):
        projected = Geometry.project_UTM_point_on_lanelet(
            projector=mgrs_projector, point=pose)

        assert abs(
            projected.x - expectation.x
        ) <= 1.0, "projected point.x is not equal to the expectation"
        assert abs(
            projected.y - expectation.y
        ) <= 1.0, "projected point.y is not equal to the expectation"


def test_geometry(lanelet_map, entities):
    basic_points = [
        BasicPoint3d(86973.4293, 41269.817, -5.6757),
        BasicPoint3d(86993.2289, 41343.5182, -4.5032),
        BasicPoint3d(87014.2461, 41427.1901, -3.2535),
        BasicPoint3d(87079.3, 41574.3, 0)
    ]

    expectations = [
        LanePosition(laneId="154", s=10.9835, offset=-0.5042),
        LanePosition(laneId="108", s=35.266, offset=-1.1844),
        LanePosition(laneId="108", s=121.5308, offset=-0.134),
        LanePosition(laneId="22", s=35.7761, offset=-0.2818)
    ]

    for idx, (basic_point,
              expectation) in enumerate(zip(basic_points, expectations)):
        Geometry.find_lanelet(lanelet_map, basic_point)
        lanelet = Geometry.find_lanelet(map=lanelet_map,
                                        basic_point=basic_point)
        assert lanelet is not None, "lanelet should not be None"

        ego_bounding_box = entities.scenarioObjects[0].entityObject.vehicle.boundingBox
        target_lane_position = Geometry.nearest_lane_position(
            map=lanelet_map,
            lanelet=lanelet,
            basic_point=basic_point,
            entity_bounding_box=ego_bounding_box)

        assert target_lane_position.laneId == expectation.laneId, "laneId should be the same"

        assert abs(
            target_lane_position.s - expectation.s
        ) <= 1.0, "s attribute should be almost equal to expectation"

        assert abs(
            target_lane_position.offset - expectation.offset
        ) <= 1.0, "t attribute should be almost equal to expectation"
