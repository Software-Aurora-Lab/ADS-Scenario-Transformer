import math
from geometry_msgs.msg import Vector3

def calculate_velocity(linear_velocity: Vector3):
    x, y, z = linear_velocity.x, linear_velocity.y, linear_velocity.z
    return round(math.sqrt(x ** 2 + y ** 2), 2)
