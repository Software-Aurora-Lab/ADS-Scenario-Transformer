import pytest
import lanelet2
from lanelet2.projection import MGRSProjector
from lanelet2.io import Origin
from lanelet2.core import LaneletMap
from modules.common.proto.geometry_pb2 import PointENU
from ads_scenario_transformer.transformer import PointENUTransformer
from ads_scenario_transformer.transformer.pointenu_transformer import PointENUTransformerConfiguration


def test_transform_world_position(lanelet_map, mgrs_projector):
    point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
    worldType = PointENUTransformer.SupportedPosition.World

    transformer = PointENUTransformer(
        configuration=PointENUTransformerConfiguration(
            supported_position=worldType,
            lanelet_map=lanelet_map,
            projector=mgrs_projector))
    position = transformer.transform(source=(point, 0.0))

    assert position.worldPosition is not None, "The gpspoint should not be None."
    assert position.worldPosition.x == 87079.30458619667
    assert position.worldPosition.y == 41574.29957442079
    assert position.worldPosition.z == 0.0


def test_transform_lane_position(lanelet_map, mgrs_projector):

    point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
    laneType = PointENUTransformer.SupportedPosition.Lane
    transformer = PointENUTransformer(
        configuration=PointENUTransformerConfiguration(
            supported_position=laneType,
            lanelet_map=lanelet_map,
            projector=mgrs_projector))

    position = transformer.transform(source=(point, 0.0))

    assert position.lanePosition is not None, "The lane_position should not be None."
    assert position.lanePosition.laneId == "22"
    assert position.lanePosition.s == 35.812947374714085
    assert position.lanePosition.offset == 0.17503992807876528
