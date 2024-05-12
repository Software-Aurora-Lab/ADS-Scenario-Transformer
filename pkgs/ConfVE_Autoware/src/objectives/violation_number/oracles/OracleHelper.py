from geometry_msgs.msg import Point
from src.tools.utils import distance


class OracleHelper:

    def __init__(self):
        self.ego_pose_pts = set()
        self.routing_plan = None

    def add_ego_pose_pt(self, p):
        self.ego_pose_pts.add(MyPoint(p))

    def set_routing_plan(self, msg):
        self.routing_plan = (msg.start_pose, msg.goal_pose)

    def has_routing_plan(self):
        return self.routing_plan is not None

    def has_enough_ego_poses(self):
        if len(self.ego_pose_pts) < 3:
            if MyPoint(self.routing_plan[0]) in self.ego_pose_pts \
                    and MyPoint(self.routing_plan[1]) in self.ego_pose_pts \
                    and distance(self.routing_plan[0], self.routing_plan[1]) < 5:
                return True
            else:
                return False
        return True


class MyPoint(Point):

    def __init__(self, point):
        super().__init__(x=point.x, y=point.y, z=point.z)

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __eq__(self, other):
        o = Point(x=other.x, y=other.y, z=other.z)
        return super().__eq__(o)

    def __repr__(self):
        return super().__repr__()
