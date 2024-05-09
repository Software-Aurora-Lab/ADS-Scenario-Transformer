from typing import Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from modules.common.proto.geometry_pb2 import PointENU
from openscenario_msgs import Position, LanePosition, WorldPosition, ScenarioObject, BoundingBox, Vehicle
from ads_scenario_transformer.transformer import Transformer
from ads_scenario_transformer.tools.geometry import Geometry
from ads_scenario_transformer.tools.vector_map_parser import VectorMapParser
from ads_scenario_transformer.builder.entities_builder import ASTEntityType


@dataclass
class PointENUTransformerConfiguration:
    supported_position: 'PointENUTransformer.SupportedPosition'
    vector_map_parser: VectorMapParser
    scenario_object: ScenarioObject
    reference_points: Optional[Tuple[PointENU, PointENU]]


@dataclass
class PointENUTransformerInput:
    point: PointENU
    heading: float


class PointENUTransformer(Transformer):
    """
    We are using LanePosition instead of WorldPosition below reason.
    - InternalError: The specified WorldPosition could not be approximated to the proper Lane. Perhaps the WorldPosition points to a location where multiple lanes overlap, and there are at least two or more candidates for a LanePosition that can be approximated to that WorldPosition. This issue can be resolved by strictly specifying the location using LanePosition instead of WorldPosition
    """
    configuration: PointENUTransformerConfiguration

    class SupportedPosition(Enum):
        Lane = 1
        World = 2

    Source = PointENUTransformerInput
    Target = Optional[Position]

    def __init__(self, configuration: PointENUTransformerConfiguration):
        self.configuration = configuration

    def transform(self, source: Source) -> Target:
        if self.configuration.supported_position == PointENUTransformer.SupportedPosition.Lane:
            lane_position = self.transformToLanePosition(source)
            return Position(lanePosition=self.transformToLanePosition(
                source)) if lane_position else None
        return Position(worldPosition=self.transformToWorldPosition(source))

    def transformToLanePosition(self,
                                source: Source) -> Optional[LanePosition]:
        vector_map_parser = self.configuration.vector_map_parser
        lanelet_map = vector_map_parser.lanelet_map
        projector = vector_map_parser.projector
        entity_type = ASTEntityType.entity_type(
            self.configuration.scenario_object)

        projected_point = Geometry.project_UTM_point_on_lanelet(
            projector=projector, point=source.point)

        lanelets = Geometry.find_close_lanelets(map=lanelet_map,
                                                basic_point=projected_point,
                                                entity_type=entity_type)

        target_lanelet = None
        if self.configuration.reference_points:
            start_point = Geometry.project_UTM_point_on_lanelet(
                projector=projector,
                point=self.configuration.reference_points[0])
            end_point = Geometry.project_UTM_point_on_lanelet(
                projector=projector,
                point=self.configuration.reference_points[-1])

            available_lane_paths = Geometry.find_available_lanes(
                vector_map_parser=vector_map_parser,
                start_point=start_point,
                end_point=end_point,
                entity_type=entity_type)

            available_lane_id = [
                lanelet.id for lanelet_path in available_lane_paths
                for lanelet in lanelet_path
            ]

            for lanelet in lanelets:
                if lanelet.id in available_lane_id:
                    target_lanelet = lanelet
                    break

        if not target_lanelet and len(lanelets) > 0:
            target_lanelet = lanelets[0]

        if target_lanelet:
            bounding_box = self.object_bouding_box(
                self.configuration.scenario_object)
            # Discard heading value
            lane_position = Geometry.nearest_lane_position(
                map=lanelet_map,
                lanelet=target_lanelet,
                basic_point=projected_point,
                entity_bounding_box=bounding_box,
                heading=0.0)
            return lane_position
        return None

    def transformToWorldPosition(self, source: Source) -> WorldPosition:
        projected_point = Geometry.project_UTM_point_on_lanelet(
            projector=self.configuration.vector_map_parser.projector,
            point=source.point)
        # Discard heading value
        return WorldPosition(x=projected_point.x,
                             y=projected_point.y,
                             z=projected_point.z,
                             h=0.0)

    def object_bouding_box(
            self, scenario_object: ScenarioObject) -> Optional[BoundingBox]:
        if scenario_object.entityObject.HasField("pedestrian"):
            return scenario_object.entityObject.pedestrian.boundingBox
        elif scenario_object.entityObject.HasField("vehicle"):
            return scenario_object.entityObject.vehicle.boundingBox
        elif scenario_object.entityObject.vehicle.vehicleCategory == Vehicle.Category.CAR:
            return scenario_object.entityObject.vehicle.boundingBox
        return None
