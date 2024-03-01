from typing import List
from openscenario_msgs import RoadNetwork, File, TrafficSignalController
from scenario_transfer.builder import Builder


class RoadNetworkBuilder(Builder):

    product: RoadNetwork

    def __init__(self,
                 lanelet_map_path: str = "lanelet_map.osm",
                 pcd_map_path: str = "point_cloud.pcd",
                 trafficSignals: List[TrafficSignalController] = []):

        lanelet_map_file = File(filepath=lanelet_map_path)
        pcd_map_file = File(filepath=pcd_map_path)

        self.product = RoadNetwork(logicFile=lanelet_map_file,
                                   sceneGraphFile=pcd_map_file,
                                   trafficSignals=trafficSignals)

    def get_result(self) -> RoadNetwork:
        return self.product
