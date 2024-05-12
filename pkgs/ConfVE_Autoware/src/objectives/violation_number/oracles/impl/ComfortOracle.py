import math
from datetime import datetime
from itertools import groupby
from typing import List, Tuple
from dataclasses import dataclass
from nav_msgs.msg import Odometry
from geometry_msgs.msg import AccelWithCovarianceStamped, Point, Vector3
from src.objectives.violation_number.oracles.OracleInterface import OracleInterface
from src.objectives.violation_number.oracles.Violation import Violation
from src.tools.autoware_tools.calculate_velocity import calculate_velocity
from src.tools.autoware_tools.time_delta import calculate_time_delta

@dataclass
class AutowareLocalization:
    pose_with_velocity: Odometry
    accl: AccelWithCovarianceStamped

    def position(self) -> Point:
        return self.pose_with_velocity.pose.pose.position

    def linear_velocity(self) -> Vector3:
        return self.pose_with_velocity.twist.twist.linear

    def linear_acceleration(self) -> Vector3:
        return self.accl.accel.accel.linear


class ComfortOracle(OracleInterface):
    """
    Comfort Oracle is responsible for checking whether fast acceleration or hard braking occurred during a scenario
    Its features include:
        * x:            float
        * y:            float
        * heading:      float
        * speed:        float
        * accel:        float
        * duration:     float
        * type:         float (1.0 => fast acceleration, -1.0 => hard braking)
    """
    pose_with_velocities: List[Tuple[float, Odometry]]
    accelerations: List[Tuple[float, AccelWithCovarianceStamped]]
    violations: List[Violation]

    MAX_ACCL = 4.0
    # MAX_DCCL = -2.5
    MAX_DCCL = -4.0
    TOLERANCE = 0.025
    # TOLERANCE = 0

    def __init__(self) -> None:
        self.pose_with_velocities = []
        self.accelerations = []
        self.violations = []
        self.trace = list()

    def get_interested_topics(self):
        return [
            '/localization/acceleration',
            '/localization/kinematic_state'
        ]

    def on_new_message(self, topic: str, message, t):
        if topic == '/localization/acceleration':
            self.accelerations.append((t, message))
        elif topic == '/localization/kinematic_state':
            self.pose_with_velocities.append((t, message))

    def mergeLocalizations(self) -> List[AutowareLocalization]:
        pose_with_velocities = self.pose_with_velocities
        accel = self.accelerations

        faster = accel if pose_with_velocities[0][0] > accel[0][0] else pose_with_velocities
        later = pose_with_velocities if faster == accel else accel

        offset = 0
        TIME_DELTA_THRESHOLD_IN_NANOSEC = 200000
        for (idx, (t, msg)) in enumerate(faster):
            delta = calculate_time_delta(msg.header.stamp, later[0][1].header.stamp)
            if abs(delta) < TIME_DELTA_THRESHOLD_IN_NANOSEC:
                offset = idx
                break
        
        result = []    
        for (idx, (t, msg)) in enumerate(faster):
            if idx + offset < len(later):
                if type(msg) == AccelWithCovarianceStamped:
                    result.append((t, AutowareLocalization(pose_with_velocity = later[idx + offset][1], accl = msg)))
                else:
                    result.append((t, AutowareLocalization(pose_with_velocity = msg, accl = later[idx + offset][1])))
        
        return result
    
    def get_accel_value(self, next_: AutowareLocalization) -> float:
        accel_x = next_.linear_acceleration().x
        accel_y = next_.linear_acceleration().y
        accel_z = next_.linear_acceleration().z

        accel_value = math.sqrt(accel_x ** 2 + accel_y ** 2 + accel_z ** 2)
        return accel_value

    def get_result(self):
        if len(self.pose_with_velocities) == 0 or len(self.accelerations) == 0:
            return []
        
        localizations = self.mergeLocalizations()

        for (_, prev_), (t2, next_) in zip(localizations, localizations[1:]):
            accel_value = self.get_accel_value(next_)

            prev_velocity = calculate_velocity(prev_.linear_velocity())
            next_velocity = calculate_velocity(next_.linear_velocity())
            direction = next_velocity - prev_velocity

            accel = accel_value * -1 if direction < 0 else accel_value
            features = self.get_basic_info_from_localization(next_.pose_with_velocity)
            features['accel'] = accel
            if accel > ComfortOracle.MAX_ACCL * (1 + ComfortOracle.TOLERANCE):
                self.trace.append((1, t2, features))
            elif accel < ComfortOracle.MAX_DCCL * (1 + ComfortOracle.TOLERANCE):
                self.trace.append((-1, t2, features))
            else:
                self.trace.append((0, t2, None))

        violations = list()
        for k, v in groupby(self.trace, key=lambda x: x[0]):
            traces = list(v)
            start_time = datetime.fromtimestamp(traces[0][1] / 1000000000)
            end_time = datetime.fromtimestamp(traces[-1][1] / 1000000000)
            delta_t = (end_time - start_time).total_seconds()
            if delta_t == 0:
                continue
            if k == 1:
                features = dict(traces[0][2])
                features['duration'] = delta_t
                features['type'] = 1.0
                violations.append(Violation(
                    'AccelOracle',
                    features,
                    str(features['accel'])
                ))
            elif k == -1:
                features = dict(traces[0][2])
                features['duration'] = delta_t
                features['type'] = -1.0
                violations.append(Violation(
                    'DecelOracle',
                    features,
                    str(features['accel'])
                ))

        return violations

