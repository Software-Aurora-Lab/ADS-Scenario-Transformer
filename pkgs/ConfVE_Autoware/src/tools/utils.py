import glob
import math
import os
import subprocess
import time
from autoware_auto_perception_msgs.msg import PredictedObject
from geometry_msgs.msg import Point, Quaternion
from src.config import ADS_ROOT, AUTOWARE_VEHICLE_LENGTH, AUTOWARE_VEHICLE_back_edge_to_center, AUTOWARE_VEHICLE_WIDTH
from shapely.geometry import Polygon, LineString
from std_msgs.msg import Header



def quaternion_2_heading(orientation: Quaternion) -> float:
    """
    Convert quaternion to heading

    Parameters:
        orientation: Quaternion
            quaternion of the car

    Returns:
        The heading value of the car

    """

    def normalize_angle(angle):
        a = math.fmod(angle + math.pi, 2.0 * math.pi)
        if a < 0.0:
            a += (2.0 * math.pi)
        return a - math.pi

    yaw = math.atan2(2.0 * (orientation.w * orientation.z - orientation.x * orientation.y),
                     2.0 * (orientation.w * orientation.w + orientation.y * orientation.y) - 1.0)
    return normalize_angle(yaw)


def generate_polygon(position: Point, theta: float, length: float, width: float):
    """
    Generate polygon for a perception obstacle

    Parameters:
        position: Point
            position vector of the obstacle
        theta: float
            heading of the obstacle
        length: float
            length of the obstacle
        width: float
            width of the obstacle

    Returns:
        points: List[Point]
            polygon points of the obstacle
    """
    points = []
    half_l = length / 2.0
    half_w = width / 2.0
    sin_h = math.sin(theta)
    cos_h = math.cos(theta)
    vectors = [(half_l * cos_h - half_w * sin_h,
                half_l * sin_h + half_w * cos_h),
               (-half_l * cos_h - half_w * sin_h,
                - half_l * sin_h + half_w * cos_h),
               (-half_l * cos_h + half_w * sin_h,
                - half_l * sin_h - half_w * cos_h),
               (half_l * cos_h + half_w * sin_h,
                half_l * sin_h - half_w * cos_h)]
    for x, y in vectors:
        p = Point()
        p.x = position.x + x
        p.y = position.y + y
        p.z = position.z
        points.append(p)
    return points


def generate_adc_polygon(position: Point, theta: float):
    """
    Generate polygon for the ADC

    Parameters:
        position: Point
            localization pose of ADC
        theta: float
            heading of ADC

    Returns:
        points: List[Point]
            polygon points of the ADC
    """
    points = []
    half_w = AUTOWARE_VEHICLE_WIDTH / 2.0
    front_l = AUTOWARE_VEHICLE_LENGTH - AUTOWARE_VEHICLE_back_edge_to_center
    back_l = -1 * AUTOWARE_VEHICLE_back_edge_to_center
    sin_h = math.sin(theta)
    cos_h = math.cos(theta)
    vectors = [(front_l * cos_h - half_w * sin_h,
                front_l * sin_h + half_w * cos_h),
               (back_l * cos_h - half_w * sin_h,
                back_l * sin_h + half_w * cos_h),
               (back_l * cos_h + half_w * sin_h,
                back_l * sin_h - half_w * cos_h),
               (front_l * cos_h + half_w * sin_h,
                front_l * sin_h - half_w * cos_h)]
    for x, y in vectors:
        p = Point()
        p.x = position.x + x
        p.y = position.y + y
        p.z = position.z
        points.append(p)
    return points


def generate_adc_rear_vertices(position: Point, theta: float):
    """
    Generate rear for the ADC

    Parameters:
        position: Point
            localization pose of ADC
        theta: float
            heading of ADC

    Returns:
        points: List[Point]
            polygon points of the ADC
    """
    points = []
    half_w = AUTOWARE_VEHICLE_WIDTH / 2.0
    back_l = -1 * AUTOWARE_VEHICLE_back_edge_to_center
    sin_h = math.sin(theta)
    cos_h = math.cos(theta)
    vectors = [(back_l * cos_h - half_w * sin_h,
                back_l * sin_h + half_w * cos_h),
               (back_l * cos_h + half_w * sin_h,
                back_l * sin_h - half_w * cos_h)]

    for x, y in vectors:
        p = Point()
        p.x = position.x + x
        p.y = position.y + y
        p.z = position.z
        points.append(p)
    return points


def obstacle_to_polygon(obs: PredictedObject) -> Polygon:
    """
    Generate polygon for the Obstacle Object

    Parameters:
        obs: PredictedObject
            predicted object of the obstacle

    Returns:
        points: Polygon
            polygon of the obstacle
    """
    if obs.shape.type == 1:
        raise NotImplementedError("Not implemented for cylinder")
    obs_heading = quaternion_2_heading(obs.kinematics.initial_pose_with_covariance.pose.orientation)
    points = []
    half_w = obs.shape.dimensions.y / 2.0
    front_l = obs.shape.dimensions.x / 2.0
    # back_l of obstacles is half of the length
    back_l = -1 * obs.shape.dimensions.x / 2.0
    sin_h = math.sin(obs_heading)
    cos_h = math.cos(obs_heading)
    vectors = [(front_l * cos_h - half_w * sin_h,
                front_l * sin_h + half_w * cos_h),
               (back_l * cos_h - half_w * sin_h,
                back_l * sin_h + half_w * cos_h),
               (back_l * cos_h + half_w * sin_h,
                back_l * sin_h - half_w * cos_h),
               (front_l * cos_h + half_w * sin_h,
                front_l * sin_h - half_w * cos_h)]
    for x, y in vectors:
        p = Point()
        p.x = obs.kinematics.initial_pose_with_covariance.pose.position.x + x
        p.y = obs.kinematics.initial_pose_with_covariance.pose.position.y + y
        p.z = obs.kinematics.initial_pose_with_covariance.pose.position.z
        points.append(p)

    return Polygon([[x.x, x.y] for x in points])

def to_Point(data):
    return Point(
        x=0.0 if math.isnan(data.x) else data.x,
        y=0.0 if math.isnan(data.y) else data.y,
        z=0.0 if math.isnan(data.z) else data.z
    )


def clean_ads_dir():
    # remove data dir
    subprocess.run(f"rm -rf {ADS_ROOT}/data".split())

    # remove records dir
    subprocess.run(f"rm -rf {ADS_ROOT}/records".split())

    # remove logs
    fileList = glob.glob(f'{ADS_ROOT}/*.log.*')
    for filePath in fileList:
        os.remove(filePath)

    # create data dir
    subprocess.run(f"mkdir {ADS_ROOT}/data".split())
    subprocess.run(f"mkdir {ADS_ROOT}/data/bag".split())
    subprocess.run(f"mkdir {ADS_ROOT}/data/log".split())
    subprocess.run(f"mkdir {ADS_ROOT}/data/core".split())
    subprocess.run(f"mkdir {ADS_ROOT}/records".split())


def calculate_velocity(linear_velocity: Point):
    x, y, z = linear_velocity.x, linear_velocity.y, linear_velocity.z
    return round(math.sqrt(x ** 2 + y ** 2), 2)


# TODO
def construct_lane_polygon(lane_msg):
    '''
    Construct the lane polygon based on their boundaries
    '''
    left_points = get_lane_boundary_points(lane_msg.left_boundary)
    right_points = get_lane_boundary_points(lane_msg.right_boundary)
    right_points.reverse()
    all_points = left_points + right_points
    return Polygon(all_points)


def get_lane_boundary_points(boundary):
    '''
    Given a lane boundary (left/right), return a list of x, y
    coordinates of all points in the boundary
    '''
    return [(pt.x, pt.y) for pt in boundary]


def construct_lane_boundary_linestring(lane):
    """
    Description: Construct two linestrings for the lane's left and right boundary
    Input: A lane message.
    Output: A list containing the linestrings representing the left and right boundary of the lane
    """
    left_boundary_points = get_lane_boundary_points(lane.leftBound)
    right_boundary_points = get_lane_boundary_points(lane.rightBound)
    return LineString(left_boundary_points), LineString(right_boundary_points)


# TODO
def find_all_files_by_wildcard(base_dir, file_name, recursive=False):
    # NOTE: combine recursive and **/ to matches all files in the current directory and in all subdirectories
    return glob.glob(join_path(base_dir, file_name), recursive=recursive)


def join_path(*args, **kwargs):
    return os.path.join(*args, **kwargs)


def get_current_timestamp():
    return round(time.time())


def get_real_time_from_msg(header: Header):
    return header.stamp.sec * 1000000000 + header.stamp.nanosec


def distance(p1: Point, p2: Point):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
