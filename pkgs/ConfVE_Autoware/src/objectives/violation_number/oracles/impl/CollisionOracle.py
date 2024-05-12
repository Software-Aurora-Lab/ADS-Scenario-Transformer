from typing import List, Optional, Tuple
from autoware_auto_perception_msgs.msg import PredictedObjects
from geometry_msgs.msg import Pose, Twist
from nav_msgs.msg import Odometry
from src.objectives.violation_number.oracles.OracleInterface import OracleInterface
from shapely.geometry import Polygon, LineString, Point
from src.objectives.violation_number.oracles.Violation import Violation
from src.tools.utils import generate_adc_polygon, quaternion_2_heading, obstacle_to_polygon
from src.tools.autoware_tools.calculate_velocity import calculate_velocity


def is_adc_responsible(front_edge: LineString, obs_polygon: Polygon) -> bool:
    return front_edge.distance(obs_polygon) == 0.0


class CollisionOracle(OracleInterface):
    """
    Collision Oracle is responsible for checking whether collision occurred between the ego vehicle and another
    road traffic participants.
    Its features include:
        x:              float
        y:              float
        heading:        float
        speed:          float
        # obs_id:         int
        obs_x:          float
        obs_y:          float
        obs_heading:    float
        obs_speed:      float
        obs_type:       int
    """
    last_localization: Optional[Odometry]
    last_perception: Optional[PredictedObjects]
    distances: List[Tuple[float, int, str]]

    def __init__(self) -> None:
        self.last_localization = None
        self.last_perception = None
        self.excluded_obs = set()
        self.violations = list()
        self.distance_traveled = 0.0

    def get_interested_topics(self):
        return [
            '/localization/kinematic_state',
            '/perception/object_recognition/objects'
        ]

    def on_new_message(self, topic: str, message, t):
        if topic == '/localization/kinematic_state':
            if self.last_localization is not None and self.oh.has_routing_plan():
                prev_point = Point(self.last_localization.pose.pose.position.x,
                                   self.last_localization.pose.pose.position.y,
                                   self.last_localization.pose.pose.position.z)
                cur_point = Point(message.pose.pose.position.x, message.pose.pose.position.y,
                                  message.pose.pose.position.z)
                self.distance_traveled += prev_point.distance(cur_point)

            self.last_localization = message
        else:
            self.last_perception = message

        if self.last_localization is None or self.last_perception is None:
            # cannot analyze
            return

        # begin analyze
        adc_pose: Pose = self.last_localization.pose.pose

        adc_heading = quaternion_2_heading(adc_pose.orientation)

        adc_polygon_pts = generate_adc_polygon(adc_pose.position, adc_heading)

        adc_front_line_string = LineString(
            [[x.x, x.y] for x in (adc_polygon_pts[0], adc_polygon_pts[3])])

        adc_polygon = Polygon([[x.x, x.y] for x in adc_polygon_pts])

        objs = self.last_perception.objects

        for obs in objs:
            obs_id = obs.object_id
            obs_id_hash = hash(obs_id.uuid.tobytes())  # numpy.ndarray is not hashable
            if obs_id_hash in self.excluded_obs:
                # obstacle may pass through ego vehicle if they are not smart
                continue

            obs_polygon = obstacle_to_polygon(obs)

            if adc_polygon.distance(obs_polygon) == 0:
                self.excluded_obs.add(obs_id_hash)

                if self.distance_traveled == 0.0 or not is_adc_responsible(adc_front_line_string, obs_polygon):
                    continue
                # collision occurred
                features = self.get_basic_info_from_localization(self.last_localization)
                # features['obs_id'] = obs_id_hash
                features['obs_x'] = obs.kinematics.initial_pose_with_covariance.pose.position.x
                features['obs_y'] = obs.kinematics.initial_pose_with_covariance.pose.position.y
                features['obs_heading'] = quaternion_2_heading(obs.kinematics.initial_pose_with_covariance.pose.orientation)
                features['obs_speed'] = calculate_velocity(obs.kinematics.initial_twist_with_covariance.twist.linear)
                features['obs_type'] = obs.classification[0].label

                self.violations.append(
                    Violation(
                        'CollisionOracle',
                        features,
                        # str(features['obs_id'])
                        str(features['obs_x'])

                )
                )

    def is_adc_completely_stopped(self) -> bool:
        adc_twist: Twist = self.last_localization.twist.twist
        adc_velocity = calculate_velocity(adc_twist.linear)
        return adc_velocity == 0

    def get_result(self):
        return self.violations
