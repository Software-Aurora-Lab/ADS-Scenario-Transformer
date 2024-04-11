from typing import List, Type
from modules.routing.proto.routing_pb2 import RoutingRequest
from openscenario_msgs import Private, ScenarioObject, Scenario
from scenario_transformer.builder import EntitiesBuilder
from scenario_transformer.builder.entities_builder import EntityType
from scenario_transformer.transformer import RoutingRequestTransformer
from scenario_transformer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel
from scenario_transformer.tools.apollo_map_parser import ApolloMapParser
from scenario_transformer.tools.vector_map_parser import VectorMapParser
from scenario_transformer.transformer.routing_request_transformer import RoutingRequestTransformerConfiguration
from scenario_transformer.builder.scenario_builder import ScenarioBuilder, ScenarioConfiguration
from scenario_transformer.builder.storyboard.init_builder import InitBuilder
from scenario_transformer.builder.storyboard.storyboard_builder import StoryboardBuilder
from scenario_transformer.builder.storyboard.trigger_builder import StopTriggerBuilder

class ScenarioTransformerConfiguration:
    apollo_scenario_path: str
    apollo_hd_map_path: str
    vector_map_path: str
    pcd_map_path: str

    def __init__(self,
                 apollo_scenario_path: str,
                 apollo_hd_map_path: str,
                 vector_map_path: str,
                 pcd_map_path: str = "point_cloud.pcd"):
        self.apollo_scenario_path = apollo_scenario_path
        self.apollo_hd_map_path = apollo_hd_map_path
        self.vector_map_path = vector_map_path
        self.pcd_map_path = pcd_map_path


class ScenarioTransformer:
    apollo_map_parser: ApolloMapParser
    vector_map_parser: VectorMapParser
    entities: List[EntityType]

    def __init__(self, configuration: ScenarioTransformerConfiguration):
        self.configuration = configuration

        self.apollo_map_parser = ApolloMapParser(
            filepath=configuration.apollo_hd_map_path)
        self.vector_map_parser = VectorMapParser(
            vector_map_path=configuration.vector_map_path)
        self.setup_entities()


    def setup_entities(self):
        self.entities = [EntityType.EGO]
        
        obstacles = CyberRecordReader.read_channel(
            source_path=self.configuration.apollo_scenario_path,
            channel=CyberRecordChannel.PERCEPTION_OBSTACLES)

        uniq_obstacles = set([(ob.id, ob.type) for obstacle in obstacles
                              for ob in obstacle.perception_obstacle])

        for id, type in uniq_obstacles:
            if type == 3:
                self.entities.append(EntityType.PEDESTRIAN)
            elif type == 5:
                self.entities.append(EntityType.NPC)

    def transform(self) -> Scenario:

        builder = EntitiesBuilder(entities=[self.entities[0]])
        ego_scenario_object = builder.get_result().scenarioObjects[0]
        
        init_builder = InitBuilder()
        ego_routing_private = self.transform_ego_routing(ego_scenario_object=ego_scenario_object)

        init_builder.make_privates(privates=[ego_routing_private])
        init = init_builder.get_result()

        stop_trigger_builder = StopTriggerBuilder()
        stop_trigger_builder.make_condition_group(conditions=[])
        stop_trigger = stop_trigger_builder.get_result()
        
        storyboard_builder = StoryboardBuilder()
        storyboard_builder.make_init(init=init)
        storyboard_builder.make_stop_trigger(trigger=stop_trigger)
        storyboard = storyboard_builder.get_result()
        
        scenario_config = ScenarioConfiguration(
            entities=self.entities,
            lanelet_map_path=self.configuration.vector_map_path,
            traffic_signals=[])
        scenario_builder = ScenarioBuilder(
            scenario_configuration=scenario_config)
        scenario_builder.make_scenario_definition(
        storyboard=storyboard,
        parameter_declarataions=[])

        return scenario_builder.get_result()
    
    def transform_ego_routing(self, ego_scenario_object: ScenarioObject) -> Private:
        routing_request_transformer = RoutingRequestTransformer(
            configuration=RoutingRequestTransformerConfiguration(
                lanelet_map=self.vector_map_parser.lanelet_map,
                projector=self.vector_map_parser.projector,
                apollo_map_parser=self.apollo_map_parser,
                ego_scenario_object=ego_scenario_object))

        routing_request = self.input_routing_request()

        return routing_request_transformer.transform(
            routing_request)

    def input_routing_request(self) -> RoutingRequest:
        """
        Read RoutingRequest channel first and then read RoutingRequest in RoutingResponse if needed
        """
        routing_requests = CyberRecordReader.read_channel(
            source_path=self.configuration.apollo_scenario_path,
            channel=CyberRecordChannel.ROUTING_REQUEST)
        if routing_requests:
            return routing_requests[0]

        routing_responses = CyberRecordReader.read_channel(
            source_path=self.configuration.apollo_scenario_path,
            channel=CyberRecordChannel.ROUTING_RESPONSE)
        routing_response = routing_responses[0]
        return routing_response.routing_request
