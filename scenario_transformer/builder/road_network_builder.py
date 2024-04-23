from typing import List
from openscenario_msgs import RoadNetwork, LogicFile, SceneGraphFile, TrafficSignals, TrafficSignalController
from scenario_transformer.builder import Builder


class RoadNetworkBuilder(Builder):

    product: RoadNetwork

    def __init__(self,
                 lanelet_map_path: str = "lanelet_map.osm",
                 pcd_map_path: str = "point_cloud.pcd",
                 trafficSignalControllers: List[TrafficSignalController] = []):

        lanelet_map_file = LogicFile(filepath=lanelet_map_path)
        pcd_map_file = SceneGraphFile(filepath=pcd_map_path)
        trafficSignals = TrafficSignals(
            trafficSignalControllers=trafficSignalControllers)

        self.product = RoadNetwork(logicFile=lanelet_map_file,
                                   sceneGraphFile=pcd_map_file,
                                   trafficSignals=trafficSignals)

    def get_result(self) -> RoadNetwork:
        return self.product
