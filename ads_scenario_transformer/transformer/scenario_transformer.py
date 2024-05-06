import math
from typing import List, Optional, Tuple
from dataclasses import dataclass
from modules.localization.proto.localization_pb2 import LocalizationEstimate
from modules.perception.proto.traffic_light_detection_pb2 import TrafficLightDetection
from modules.routing.proto.routing_pb2 import RoutingRequest
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles
from openscenario_msgs import Private, ScenarioObject, Scenario, Entities, Story, RoutingAction
from ads_scenario_transformer.builder import EntitiesBuilder
from ads_scenario_transformer.builder.entities_builder import ASTEntityType, ASTEntity
from ads_scenario_transformer.transformer import RoutingRequestTransformer
from ads_scenario_transformer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel
from ads_scenario_transformer.tools.apollo_map_parser import ApolloMapParser
from ads_scenario_transformer.tools.vector_map_parser import VectorMapParser
from ads_scenario_transformer.transformer.pointenu_transformer import PointENUTransformer, PointENUTransformerConfiguration
from ads_scenario_transformer.transformer.routing_request_transformer import RoutingRequestTransformerConfiguration
from ads_scenario_transformer.transformer.obstacles_transformer import ObstaclesTransformer, ObstaclesTransformerConfiguration, ObstaclesTransformerResult
from ads_scenario_transformer.builder.scenario_builder import ScenarioBuilder, ScenarioConfiguration
from ads_scenario_transformer.builder.storyboard.init_builder import InitBuilder
from ads_scenario_transformer.builder.storyboard.storyboard_builder import StoryboardBuilder
from ads_scenario_transformer.builder.storyboard.story_builder import StoryBuilder
from ads_scenario_transformer.builder.storyboard.trigger_builder import StopTriggerBuilder
from ads_scenario_transformer.transformer.traffic_signal_transformer import TrafficSignalTransformer, TrafficSignalTransformerConfiguration, TrafficSignalTransformerResult
from ads_scenario_transformer.tools.error import InvalidScenarioInputError
from ads_scenario_transformer.tools.map_cache import MapCache


@dataclass
class ScenarioTransformerConfiguration:
    apollo_scenario_path: str
    apollo_hd_map_path: str
    vector_map_path: str
    road_network_pcd_map_path: str
    road_network_lanelet_map_path: str
    obstacle_waypoint_frequency_in_sec: Optional[float]
    obstacle_direction_change_detection_threshold: float  # 0 ~ 360 degree, Will be used if obstacle_waypoint_frequency_in_sec is None
    disable_traffic_signal: bool
    use_last_position_as_destination: bool  # if True, the destination is the last position of the ego in LocalizationPose chanel, otherwise, the ego destination becomes the last position in routing request

    def __init__(self,
                 apollo_scenario_path: str,
                 apollo_hd_map_path: str,
                 vector_map_path: str,
                 use_last_position_as_destination: bool,
                 obstacle_waypoint_frequency_in_sec: Optional[float],
                 disable_traffic_signal: bool = False,
                 obstacle_direction_change_detection_threshold=60,
                 road_network_lanelet_map_path: Optional[str] = None,
                 road_network_pcd_map_path: str = "point_cloud.pcd"):
        self.apollo_scenario_path = apollo_scenario_path
        self.apollo_hd_map_path = apollo_hd_map_path
        self.vector_map_path = vector_map_path
        self.obstacle_waypoint_frequency_in_sec = obstacle_waypoint_frequency_in_sec
        self.obstacle_direction_change_detection_threshold = obstacle_direction_change_detection_threshold
        self.use_last_position_as_destination = use_last_position_as_destination
        self.disable_traffic_signal = disable_traffic_signal
        if road_network_lanelet_map_path:
            self.road_network_lanelet_map_path = road_network_lanelet_map_path
        else:
            self.road_network_lanelet_map_path = vector_map_path
        self.road_network_pcd_map_path = road_network_pcd_map_path


class ScenarioTransformer:
    apollo_map_parser: ApolloMapParser
    vector_map_parser: VectorMapParser
    entities: Entities
    localization_poses: List[LocalizationEstimate]
    routing_request: Optional[RoutingRequest]
    obstacles: Optional[PerceptionObstacles]
    traffic_light_detections: List[TrafficLightDetection]

    def __init__(self, configuration: ScenarioTransformerConfiguration):
        self.configuration = configuration

        self.apollo_map_parser = MapCache.get_apollo_map_parser(
            apollo_hd_map_path=configuration.apollo_hd_map_path)
        self.vector_map_parser = MapCache.get_vector_map_parser(
            vector_map_path=configuration.vector_map_path)

        self.localization_poses = []
        self.routing_request = None
        self.obstacles = []
        self.traffic_light_detections = []
        self.input_localization()

    def transform(self) -> Scenario:
        transformed_obstacle_result = self.transform_obstacle_movements()
        obstacles = [
            meta for meta, obj in transformed_obstacle_result.entities_with_id
        ]
        self.setup_entities(obstacles=obstacles)

        init_builder = InitBuilder()
        ego_routing_private = self.transform_ego_routing(
            ego_scenario_object=self.entities.scenarioObjects[0])

        init_builder.make_privates(privates=[ego_routing_private])
        init = init_builder.get_result()

        stop_trigger_builder = StopTriggerBuilder()
        stop_trigger_builder.make_condition_group(conditions=[])
        stop_trigger = stop_trigger_builder.get_result()

        storyboard_builder = StoryboardBuilder()
        storyboard_builder.make_init(init=init)
        storyboard_builder.make_stop_trigger(trigger=stop_trigger)

        default_end_story = self.setup_default_end_story(
            routing_action=ego_routing_private.privateActions[1].routingAction)

        storyboard_builder.make_stories(
            stories=transformed_obstacle_result.stories + [default_end_story])
        storyboard = storyboard_builder.get_result()

        traffic_signals = []
        if not self.configuration.disable_traffic_signal:
            traffic_signal_result = self.transform_traffic_environment()
            traffic_signals = traffic_signal_result.road_network_traffic

        scenario_config = ScenarioConfiguration(
            entities=self.entities,
            lanelet_map_path=self.configuration.road_network_lanelet_map_path,
            traffic_signals=traffic_signals)
        scenario_builder = ScenarioBuilder(
            scenario_configuration=scenario_config)
        scenario_builder.make_scenario_definition(storyboard=storyboard,
                                                  parameter_declarataions=[])

        return scenario_builder.get_result()

    def setup_entities(self, obstacles: List[ASTEntity]):
        entities_builder = EntitiesBuilder()
        for obstacle in obstacles:
            entities_builder.add_entity(ast_entity=obstacle)
        self.entities = entities_builder.get_result()

    def setup_default_end_story(self, routing_action: RoutingAction) -> Story:

        ego_end_position = None
        if self.configuration.use_last_position_as_destination:
            last_pose = self.localization_poses[-1].pose.position
            pointenu_transformer = PointENUTransformer(
                configuration=PointENUTransformerConfiguration(
                    supported_position=PointENUTransformer.SupportedPosition.
                    Lane,
                    lanelet_map=self.vector_map_parser.lanelet_map,
                    projector=self.vector_map_parser.projector,
                    lanelet_subtypes=ASTEntityType.EGO.
                    available_lanelet_subtype(),
                    scenario_object=self.entities.scenarioObjects[0]))
            ego_end_position = pointenu_transformer.transform((last_pose, 0.0))
        else:
            if routing_action.HasField("assignRouteAction"):
                ego_end_position = routing_action.assignRouteAction.route.waypoints[
                    -1].position
            else:
                ego_end_position = routing_action.acquirePositionAction.position

        assert ego_end_position is not None

        total_duration = math.ceil(self.scenario_end_time -
                                   self.scenario_start_time)
        return StoryBuilder.default_end_story(
            entities=self.entities,
            ego_end_position=ego_end_position,
            exit_failure_duration=total_duration)

    def transform_obstacle_movements(self) -> ObstaclesTransformerResult:
        obstacles = self.input_perception_obstacles()

        obstacles_transformer = ObstaclesTransformer(
            configuration=ObstaclesTransformerConfiguration(
                sceanrio_start_timestamp=self.scenario_start_time,
                lanelet_map=self.vector_map_parser.lanelet_map,
                projector=self.vector_map_parser.projector,
                waypoint_frequency_in_sec=self.configuration.
                obstacle_waypoint_frequency_in_sec,
                direction_change_detection_threshold=self.configuration.
                obstacle_direction_change_detection_threshold))

        return obstacles_transformer.transform(source=obstacles)

    def transform_ego_routing(self,
                              ego_scenario_object: ScenarioObject) -> Private:
        routing_request_transformer = RoutingRequestTransformer(
            configuration=RoutingRequestTransformerConfiguration(
                lanelet_map=self.vector_map_parser.lanelet_map,
                projector=self.vector_map_parser.projector,
                apollo_map_parser=self.apollo_map_parser,
                ego_scenario_object=ego_scenario_object))

        routing_request = self.input_routing_request()

        return routing_request_transformer.transform(routing_request)

    def transform_traffic_environment(self) -> TrafficSignalTransformerResult:
        traffic_signal_transformer = TrafficSignalTransformer(
            configuration=TrafficSignalTransformerConfiguration(
                vector_map_parser=self.vector_map_parser,
                apollo_map_parser=self.apollo_map_parser))

        traffic_light_detections = self.input_traffic_light_detections()
        return traffic_signal_transformer.transform(traffic_light_detections)

    def input_routing_request(self) -> RoutingRequest:
        """
        Read RoutingRequest channel first and then read RoutingRequest in RoutingResponse if needed
        """
        if self.routing_request:
            return self.routing_request

        routing_requests = CyberRecordReader.read_channel(
            source_path=self.configuration.apollo_scenario_path,
            channel=CyberRecordChannel.ROUTING_REQUEST)
        if routing_requests:
            self.routing_request = routing_requests[0]
            return self.routing_request

        routing_responses = CyberRecordReader.read_channel(
            source_path=self.configuration.apollo_scenario_path,
            channel=CyberRecordChannel.ROUTING_RESPONSE)
        routing_response = routing_responses[0]

        self.routing_request = routing_response.routing_request

        if not self.routing_request:
            raise InvalidScenarioInputError(
                "No RoutingRequest found in scenario")

        return self.routing_request

    def input_perception_obstacles(self) -> List[PerceptionObstacles]:
        if self.obstacles:
            return self.obstacles

        self.obstacles = CyberRecordReader.read_channel(
            source_path=self.configuration.apollo_scenario_path,
            channel=CyberRecordChannel.PERCEPTION_OBSTACLES)

        return self.obstacles

    def input_traffic_light_detections(self) -> List[TrafficLightDetection]:
        if self.traffic_light_detections:
            return self.traffic_light_detections

        self.traffic_light_detections = CyberRecordReader.read_channel(
            source_path=self.configuration.apollo_scenario_path,
            channel=CyberRecordChannel.TRAFFIC_LIGHT)

        return self.traffic_light_detections

    def input_localization(self) -> List[LocalizationEstimate]:

        if self.localization_poses:
            return self.localization_poses

        self.localization_poses = CyberRecordReader.read_channel(
            source_path=self.configuration.apollo_scenario_path,
            channel=CyberRecordChannel.LOCALIZATION_POSE)

        if not self.localization_poses:
            raise InvalidScenarioInputError(
                "No localization poses found in scenario")

        self.scenario_start_time = self.localization_poses[
            0].header.timestamp_sec
        self.scenario_end_time = self.localization_poses[
            -1].header.timestamp_sec

        return self.localization_poses
