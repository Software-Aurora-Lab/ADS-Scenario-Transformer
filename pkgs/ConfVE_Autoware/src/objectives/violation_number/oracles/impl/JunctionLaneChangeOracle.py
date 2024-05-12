from typing import List, Optional
from geometry_msgs.msg import Pose
from lanelet2.core import Lanelet, BasicPoint2d
from lanelet2.geometry import inside
from src.objectives.violation_number.oracles.OracleInterface import OracleInterface
from src.objectives.violation_number.oracles.Violation import Violation
from src.tools.hdmap.VectorMapParser import VectorMapParser

class JunctionLaneChangeOracle(OracleInterface):
    """
    Junction Lane Change Oracle is responsible for checking if the ADS makes a lane-change decision while inside a
    junction.
        * x:            float
        * y:            float
        * heading:      float
        * speed:        float
        * junction_id:  int     # index of junction_id in a sorted list
    """

    def __init__(self) -> None:
        super().__init__()
        self.map_parser = VectorMapParser.instance()
        self.junctions = self.map_parser.get_all_intersections()
        self.junction_type_lanelets = self.map_parser.get_lanelets(identifiers=[junction_id for junction_id in self.junctions.keys()])
        self.last_localization = None
        self.violation = list()

    def get_interested_topics(self) -> List[str]:
        return [
            '/localization/kinematic_state',
            '/planning/path_candidate/lane_change_left',
            '/planning/path_candidate/lane_change_right'
        ]

    def current_junction_type_lanelet(self, pose: Pose) -> Optional[Lanelet]:
        point = BasicPoint2d(pose.position.x, pose.position.y)
        for lanelet in self.junction_type_lanelets:
          if inside(lanelet, point):
              return lanelet
        return None
        
    def on_new_message(self, topic: str, message, t):
        if len(self.violation) > 0:
            # violation already tracked
            return
        if topic == '/localization/kinematic_state':
            self.on_localization(message)
        else:
            self.on_lane_change(message)

    def on_lane_change(self, message):
        if self.last_localization is None:
            return

        # Path becomes not empty when ego car starts lane changing 
        path = message.points
        if not path:
            return

        current_lanelet = self.current_junction_type_lanelet(pose=self.last_localization.pose.pose)
        if not current_lanelet:
            return

        features = self.get_basic_info_from_localization(self.last_localization)
        features['junction_id'] = current_lanelet.id
        self.violation.append(Violation(
            'JunctionLaneChangeOracle',
            features,
            str(features['junction_id'])
        ))

    def on_localization(self, message):
        self.last_localization = message

    def get_result(self):
        return self.violation
