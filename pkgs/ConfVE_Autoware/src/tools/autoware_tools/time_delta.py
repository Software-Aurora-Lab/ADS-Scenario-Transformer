from datetime import datetime, timedelta

from rclpy.time import Time

def calculate_time_delta(time1: Time, time2: Time) -> float:
    def epoch_time_to_datetime(epoch_time_sec, epoch_time_nsec):
        # Convert epoch time to datetime
       return datetime.utcfromtimestamp(epoch_time_sec) + timedelta(microseconds=epoch_time_nsec / 1000)

    dt1 = epoch_time_to_datetime(time1.sec, time1.nanosec)
    dt2 = epoch_time_to_datetime(time2.sec, time2.nanosec)
    delta = dt2 - dt1
    return delta.total_seconds() * 1e9

