from typing import List, Optional, Tuple
from modules.perception.proto.traffic_light_detection_pb2 import TrafficLightDetection
from modules.routing.proto.routing_pb2 import RoutingRequest
from modules.perception.proto.perception_obstacle_pb2 import PerceptionObstacles
from openscenario_msgs import Private, ScenarioObject, Scenario, Entities, Story
from scenario_transformer.builder import EntitiesBuilder
from scenario_transformer.builder.entities_builder import EntityType, EntityMeta
from scenario_transformer.transformer import RoutingRequestTransformer
from scenario_transformer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel
from scenario_transformer.tools.apollo_map_parser import ApolloMapParser
from scenario_transformer.tools.vector_map_parser import VectorMapParser
from scenario_transformer.transformer.routing_request_transformer import RoutingRequestTransformerConfiguration
from scenario_transformer.transformer.obstacles_transformer import ObstaclesTransformer, ObstaclesTransformerConfiguration, ObstaclesTransformerResult
from scenario_transformer.builder.scenario_builder import ScenarioBuilder, ScenarioConfiguration
from scenario_transformer.builder.storyboard.init_builder import InitBuilder
from scenario_transformer.builder.storyboard.storyboard_builder import StoryboardBuilder
from scenario_transformer.builder.storyboard.story_builder import StoryBuilder
from scenario_transformer.builder.storyboard.trigger_builder import StopTriggerBuilder
from scenario_transformer.transformer.traffic_signal_transformer import TrafficSignalTransformer, TrafficSignalTransformerConfiguration, TrafficSignalTransformerResult


class ScenarioTransformerConfiguration:
    apollo_scenario_path: str
    apollo_hd_map_path: str
    vector_map_path: str
    pcd_map_path: str
    enable_traffic_signal: bool

    def __init__(self,
                 apollo_scenario_path: str,
                 apollo_hd_map_path: str,
                 vector_map_path: str,
                 enable_traffic_signal: bool = True,
                 road_network_lanelet_map_path: Optional[str] = None,
                 pcd_map_path: str = "point_cloud.pcd"):
        self.apollo_scenario_path = apollo_scenario_path
        self.apollo_hd_map_path = apollo_hd_map_path
        self.vector_map_path = vector_map_path
        self.enable_traffic_signal = enable_traffic_signal
        if road_network_lanelet_map_path:
            self.road_network_lanelet_map_path = road_network_lanelet_map_path
        else:
            self.road_network_lanelet_map_path = vector_map_path
        self.pcd_map_path = pcd_map_path


class ScenarioTransformer:
    apollo_map_parser: ApolloMapParser
    vector_map_parser: VectorMapParser
    entities: Entities
    routing_request: Optional[RoutingRequest]
    obstacles: Optional[PerceptionObstacles]
    traffic_light_detections: List[TrafficLightDetection]

    def __init__(self, configuration: ScenarioTransformerConfiguration):
        self.configuration = configuration

        self.apollo_map_parser = ApolloMapParser(
            filepath=configuration.apollo_hd_map_path)
        self.vector_map_parser = VectorMapParser(
            vector_map_path=configuration.vector_map_path)
        self.routing_request = None
        self.obstacles = None
        self.traffic_light_detections = []

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

        default_end_story = StoryBuilder.default_end_story(
            entities=self.entities,
            routing_action=ego_routing_private.privateActions[1].routingAction)

        storyboard_builder.make_stories(
            stories=transformed_obstacle_result.stories + [default_end_story])
        storyboard = storyboard_builder.get_result()

        traffic_signals = []
        if self.configuration.enable_traffic_signal:
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

    def setup_entities(self, obstacles: List[EntityMeta]):
        entity_meta = [EntityMeta(entity_type=EntityType.EGO)] + obstacles
        entities_builder = EntitiesBuilder(entities=entity_meta)
        self.entities = entities_builder.get_result()

    def transform_obstacle_movements(self) -> ObstaclesTransformerResult:
        obstacles = self.input_perception_obstacles()

        sceanrio_start_timestamp = obstacles[0].header.timestamp_sec
        obstacles_transformer = ObstaclesTransformer(
            configuration=ObstaclesTransformerConfiguration(
                sceanrio_start_timestamp=sceanrio_start_timestamp,
                lanelet_map=self.vector_map_parser.lanelet_map,
                projector=self.vector_map_parser.projector))

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
