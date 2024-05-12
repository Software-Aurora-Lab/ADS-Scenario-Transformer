from datetime import datetime
from itertools import groupby
from typing import List
from lanelet2.core import BasicPoint2d, BasicPoint3d
from lanelet2.geometry import inside
from src.objectives.violation_number.oracles.OracleInterface import OracleInterface
from src.objectives.violation_number.oracles.Violation import Violation
from src.tools.hdmap.VectorMapParser import VectorMapParser
from src.tools.autoware_tools.calculate_velocity import calculate_velocity


class SpeedingOracle(OracleInterface):
    """
    Speeding Oracle is responsible for checking if the ego vehicle violates speed limit at any point
    Its features include:
        * x:            float
        * y:            float
        * heading:      float
        * speed:        float
        * speed_limit:  float
        * duration:     float
    """

    TOLERANCE = 0.025
    # TOLERANCE = 0

    def __init__(self) -> None:
        self.map_parser = VectorMapParser.instance()
        self.lanelet_speed_limits = self.map_parser.get_attributes("speed_limit", float)
        self.min_speed_limit = min(self.lanelet_speed_limits.values())
        self.trace = list()

    def get_interested_topics(self) -> List[str]:
        return ['/localization/kinematic_state']

    def on_new_message(self, topic: str, message, t):
        ego_position = message.pose.pose.position
        ego_velocity = calculate_velocity(message.twist.twist.linear) * 3.6
        
        if ego_velocity <= self.min_speed_limit * (1 + SpeedingOracle.TOLERANCE):
            # cannot violate any speed limit
            self.trace.append((False, t, -1, dict()))
            return

        point = BasicPoint2d(ego_position.x, ego_position.y)
        for lanelet in self.map_parser.lanelet_map.laneletLayer:
          if inside(lanelet, point):
            lane_speed_limit = self.lanelet_speed_limits[lanelet.id]
            if ego_velocity > lane_speed_limit * (1 + SpeedingOracle.TOLERANCE):
              features = self.get_basic_info_from_localization(message)
              features['speed_limit'] = lane_speed_limit
              self.trace.append((True, t, lane_speed_limit, features))
              return
        self.trace.append((False, t, -1, dict()))

    def get_result(self):
        violations = list()
        for k, v in groupby(self.trace, key=lambda x: (x[0], x[2])):
            traces = list(v)
            start_time = datetime.fromtimestamp(traces[0][1] / 1000000000)
            end_time = datetime.fromtimestamp(traces[-1][1] / 1000000000)
            delta_t = (end_time - start_time).total_seconds()

            if k[0]:
                features = dict(traces[0][3])
                features['duration'] = delta_t
                violations.append(Violation(
                    'SpeedingOracle',
                    features,
                    str(features['speed'])
                ))

        return violations

