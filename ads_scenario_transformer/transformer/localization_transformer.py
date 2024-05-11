from typing import Optional, List
from dataclasses import dataclass
from modules.localization.proto.localization_pb2 import LocalizationEstimate
from modules.common.proto.geometry_pb2 import PointENU
from openscenario_msgs import Private, ScenarioObject, Position
from ads_scenario_transformer.transformer import Transformer
from ads_scenario_transformer.builder.private_builder import PrivateBuilder
from ads_scenario_transformer.tools.apollo_map_parser import ApolloMapParser
from ads_scenario_transformer.tools.vector_map_parser import VectorMapParser
from ads_scenario_transformer.transformer.pointenu_transformer import PointENUTransformer, PointENUTransformerConfiguration, PointENUTransformerInput


@dataclass
class LocalizationTransformerConfiguration:
    vector_map_parser: VectorMapParser
    apollo_map_parser: ApolloMapParser
    ego_scenario_object: ScenarioObject


class LocalizationTransformer(Transformer):
    configuiration: LocalizationTransformerConfiguration
    Source = List[LocalizationEstimate]
    Target = Private

    def __init__(self, configuration: LocalizationTransformerConfiguration):
        self.configuration = configuration

    def transform(self, source: Source) -> Private:
        assert len(source) > 1

        start_point = source[0].pose.position
        end_point = source[-1].pose.position

        start_position = self.transform_coordinate_value(
            point=start_point, start_point=start_point, end_point=end_point)

        end_position = self.transform_coordinate_value(point=end_point,
                                                       start_point=start_point,
                                                       end_point=end_point)

        private_builder = PrivateBuilder(
            scenario_object=self.configuration.ego_scenario_object)

        private_builder.make_routing_action_with_positions(
            positions=[start_position, end_position],
            closed=False,
            name="LocalizationTransformer Generated Route")

        return private_builder.get_result()

    def transform_coordinate_value(self, point: PointENU,
                                   start_point: PointENU,
                                   end_point: PointENU) -> Optional[Position]:

        transformer = PointENUTransformer(
            configuration=PointENUTransformerConfiguration(
                supported_position=PointENUTransformer.SupportedPosition.Lane,
                vector_map_parser=self.configuration.vector_map_parser,
                scenario_object=self.configuration.ego_scenario_object,
                reference_points=[start_point, end_point]))

        position = transformer.transform(
            source=PointENUTransformerInput(point, 0.0))
        return position
