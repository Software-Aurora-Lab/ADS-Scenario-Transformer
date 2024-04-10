

import lanelet2
from lanelet2.projection import MGRSProjector
from lanelet2.io import Origin
from openscenario_msgs import Private, TeleportAction, RoutingAction, AssignRouteAction
from scenario_transfer.transformer import RoutingRequestTransformer
from scenario_transfer.tools.apollo_map_service import ApolloMapService
from scenario_transfer.builder import EntitiesBuilder
from scenario_transfer.builder.entities_builder import EntityType
from scenario_transfer.openscenario import OpenScenarioEncoder
from scenario_transfer.tools.cyber_record_reader import CyberRecordReader, CyberRecordChannel

from scenario_transfer.tools.apllo_map_parser import ApolloMapParser
from scenario_transfer.tools.vector_map_parser import VectorMapParser


class ScenarioTransformerConfiguration:
    entities: List[EntityType]
    apollo_hd_map_path: str
    vector_map_path: str
    pcd_map_path: str
    traffic_signals: List[TrafficSignalController]

    def __init__(self,
                 apollo_scenario_path: str,
                 apollo_hd_map_path: str,
                 vector_map_path: str,
                 pcd_map_path: str = "point_cloud.pcd"):
        self.apollo_hd_map_path = apollo_hd_map_path
        self.vector_map_path = vector_map_path
        self.pcd_map_path = pcd_map_path

    
class ScenarioTransformer:
    apollo_map_parser: ApolloMapParser
    vector_map_parser: VectorMapParser
    
    def __init__(self, configuration: ScenarioTransformerConfiguration):
        self.configuration = configuration
        
        apollo_scenario_path

        CyberRecordReader.read_channel
        self.apollo_map_parser = ApolloMapParser(filepath=configuration.apollo_hd_map_path)
        self.vector_map_parser = VectorMapParser(vector_map_path=configuration.vector_map_path)

    def transform_routing(self):
        routing_requests = CyberRecordReader.read_channel(
            source_path=self.configuration.apollo_scenario_path,
            channel=CyberRecordChannel.ROUTING_REQUEST)


# routing_request_transformer = RoutingRequestTransformer(
#     properties={
#         "lanelet_map": self.lanelet_map,
#         "projector": self.mgrs_Projector,
#         "apollo_map_service": self.apollo_map_service,
#         "route_name": "test_route",
#         "ego_scenario_object": self.ego
#     })

# routing_requests = CyberRecordReader.read_channel(
#     source_path="./samples/apollo_borregas/00000009.00000",
#     channel=CyberRecordChannel.ROUTING_REQUEST)

# routing_request = routing_requests[0]
# openscenario_private = routing_request_transformer.transform(
#     routing_request)
        