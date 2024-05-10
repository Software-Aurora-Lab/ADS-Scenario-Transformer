from modules.common.proto.geometry_pb2 import PointENU
from ads_scenario_transformer.transformer import PointENUTransformer
from ads_scenario_transformer.transformer.pointenu_transformer import PointENUTransformerConfiguration, PointENUTransformerInput
from ads_scenario_transformer.builder.entities_builder import ASTEntityType, ASTEntity
from ads_scenario_transformer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel


def test_transform_world_position(localization_poses, vector_map_parser,
                                  entities):
    point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
    worldType = PointENUTransformer.SupportedPosition.World

    transformer = PointENUTransformer(
        configuration=PointENUTransformerConfiguration(
            supported_position=worldType,
            vector_map_parser=vector_map_parser,
            scenario_object=entities.scenarioObjects[0],
            reference_points=None))
    position = transformer.transform(
        source=PointENUTransformerInput(point, 0.0))

    assert position.worldPosition is not None, "The gpspoint should not be None."
    assert position.worldPosition.x == 87079.30458619667
    assert position.worldPosition.y == 41574.29957442079
    assert position.worldPosition.z == 0.0


def test_transform_lane_position(localization_poses, vector_map_parser,
                                 entities):

    point = PointENU(x=587079.3045861976, y=4141574.299574421, z=0)
    laneType = PointENUTransformer.SupportedPosition.Lane
    transformer = PointENUTransformer(
        configuration=PointENUTransformerConfiguration(
            supported_position=laneType,
            vector_map_parser=vector_map_parser,
            scenario_object=entities.scenarioObjects[0],
            reference_points=None))

    position = transformer.transform(
        source=PointENUTransformerInput(point, 0.0))

    assert position.lanePosition is not None, "The lane_position should not be None."
    assert position.lanePosition.laneId == "22"
    assert position.lanePosition.s == 35.812947374714085
    assert position.lanePosition.offset == 0.0


def test_geometry_in_routing3(vector_map_parser, apollo_map_parser,
                              borregas_scenorita_scenario94_path, entities):

    localization_poses = CyberRecordReader.read_channel(
        source_path=borregas_scenorita_scenario94_path,
        channel=CyberRecordChannel.LOCALIZATION_POSE)

    last_point = localization_poses[-1].pose.position

    laneType = PointENUTransformer.SupportedPosition.Lane
    transformer = PointENUTransformer(
        configuration=PointENUTransformerConfiguration(
            supported_position=laneType,
            vector_map_parser=vector_map_parser,
            scenario_object=entities.scenarioObjects[0],
            reference_points=[
                localization_poses[0].pose.position,
                localization_poses[-1].pose.position
            ]))

    position = transformer.transform(
        source=PointENUTransformerInput(last_point, 0.0))

    assert position.lanePosition.laneId == "104"
