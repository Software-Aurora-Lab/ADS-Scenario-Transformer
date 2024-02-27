from openscenario_msgs import RoadNetwork
from scenario_transfer.builder import Builder


class RoadNetworkBuilder(Builder):

    def __init__(self):
        pass

    def get_result(self) -> RoadNetwork:
        return RoadNetwork()
