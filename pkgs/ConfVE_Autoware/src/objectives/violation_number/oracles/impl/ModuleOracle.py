from typing import Optional
from shapely.geometry import Point
from src.objectives.violation_number.oracles.OracleInterface import OracleInterface
from src.objectives.violation_number.oracles.Violation import Violation
from nav_msgs.msg import Odometry
from autoware_auto_planning_msgs.msg import Trajectory


class ModuleOracle(OracleInterface):
    """
    Module Oracle is responsible for checking and categorizing module failures
    Its features include:
        # * x: float
        # * y: float
        # * heading: float
        # * speed: float
        # * type: int

    Error code for type includes:
        * 400: Routing Failure
        * 401: Prediction Failure
        * 402: Planning Failure

        * 500: Car never moved
        * 501: Planning generates garbage

        * 600: LocalizationFailure
        * 700: SimulationFailure
    """
    distance_traveled: float

    def __init__(self) -> None:
        self.prev_: Optional[Odometry] = None
        self.next_: Optional[Odometry] = None
        self.last_localization: Optional[Odometry] = None

        self.received_routing: bool = False
        self.received_planning: bool = False
        self.received_prediction: bool = False
        self.received_localization: bool = False

        self.has_normal_planning_decision: bool = False
        self.distance_traveled = 0

    def get_interested_topics(self):
        return [
            '/planning/mission_planning/route',
            '/planning/scenario_planning/trajectory',
            '/perception/object_recognition/objects',
            '/localization/kinematic_state',
        ]

    def on_new_message(self, topic: str, message, t):
        if topic == '/planning/mission_planning/route':
            self.received_routing = True
        if topic == '/perception/object_recognition/objects':
            self.received_prediction = True
        if topic == '/planning/scenario_planning/trajectory':
            self.received_planning = True
            if not self.has_normal_planning_decision:
                self.last_planning: Trajectory = message
                if self.is_adc_planner_making_normal_decision():
                    self.has_normal_planning_decision = True
        if topic == '/localization/kinematic_state':
            if not self.oh.has_routing_plan():
                return
            self.received_localization = True
            self.last_localization = message
            if self.prev_ is None and self.next_ is None:
                self.prev_ = message
                return
            self.next_ = message
            prev_point = Point(self.prev_.pose.pose.position.x, self.prev_.pose.pose.position.y, self.prev_.pose.pose.position.z)
            next_point = Point(self.next_.pose.pose.position.x, self.next_.pose.pose.position.y, self.next_.pose.pose.position.z)
            self.distance_traveled += prev_point.distance(next_point)

    def is_adc_planner_making_normal_decision(self):
        traj_pts = self.last_planning.points

        if len(traj_pts) == 0:
            return False
        first_pt = traj_pts[0]
        for pt in traj_pts[1:]:
            if pt != first_pt:
                return True
        return False

    def get_result(self):
        result = list()
        if self.received_localization:
            feature = self.get_basic_info_from_localization(self.last_localization)
            if not self.received_routing:
                vf = dict(feature)
                vf['type'] = 400
                result.append(Violation(
                    'RoutingFailure', vf, str(vf['type'])
                ))
            if not self.received_prediction:
                vf = dict(feature)
                vf['type'] = 401
                result.append(Violation(
                    'PredictionFailure', vf, str(vf['type'])
                ))
            if not self.received_planning:
                vf = dict(feature)
                vf['type'] = 402
                result.append(Violation(
                    'PlanningFailure', vf, str(vf['type'])
                ))

            if self.received_planning and self.received_routing and self.received_prediction:
                if self.distance_traveled == 0:
                    if self.has_normal_planning_decision:
                        vf = dict(feature)
                        vf['type'] = 500
                        result.append(Violation(
                            'CarNeverMoved', vf, str(vf['type'])
                        ))
                    else:
                        vf = dict(feature)
                        vf['type'] = 501
                        result.append(Violation(
                            'PlanningGeneratesGarbage', vf, str(vf['type'])
                        ))
        else:
            if self.received_planning and self.received_routing and self.received_prediction:
                vf = dict()
                vf['type'] = 600
                result.append(Violation(
                    'LocalizationFailure', vf, str(vf['type'])
                ))

        if not self.oh.has_routing_plan() or not self.oh.has_enough_ego_poses() and len(result) == 0:
            vf = dict()
            vf['type'] = 700
            return [
                Violation('SimulationFailure', vf, str(vf['type']))
            ]
        return result
