import os
from typing import Set, Tuple, List
from shapely import LineString
from src.config import ADS_SCENARIO_DIR, ADS_RECORDS_DIR
from scenario_handling.Scenario import Scenario
from src.tools.autoware_tools.rosbag_reader import ROSBagReader


def analyze_decision(record_dir):
    record = ROSBagReader(record_dir)
    decisions: Set[Tuple] = set()
    decision_related_topics = ["/planning/velocity_factors", "/planning/steering_factor"]
    for topic, message, t in record.read_messages():
        for topic_name in decision_related_topics:
            if topic_name in topic:
                msg = record.deserialize_msg(message, topic)
                factors_list = msg.factors
                if len(factors_list) > 0:
                    for factor in factors_list:
                        decisions.add(factor.behavior)
    decision_count = len(decisions)
    return decision_count


def analyze_sinuosity(record_dir):
    record = ROSBagReader(record_dir)
    coordinates: List[Tuple[float, float]] = list()
    for _, msg, t in record.read_specific_messages("/localization/kinematic_state"):
        new_coordinate = (msg.pose.pose.position.x, msg.pose.pose.position.y)
        # print(new_coordinate)
        if len(coordinates) > 0 and coordinates[-1] == new_coordinate:
            continue
        else:
            coordinates.append(new_coordinate)
            # print(new_coordinate)
    if len(coordinates) < 3:
        sinuosity = 0
    else:
        ego_trajectory = LineString(coordinates)
        start_point = ego_trajectory.interpolate(0, normalized=True)
        end_point = ego_trajectory.interpolate(1, normalized=True)
        shortest_path = LineString([start_point, end_point])
        if shortest_path.length == 0:
            sinuosity = 0
        else:
            sinuosity = ego_trajectory.length / shortest_path.length
    return sinuosity


if __name__ == '__main__':
    record_name = "7c28b88b-e5f3-46e7-8311-d3b34aff9254"

    scenario = Scenario(record_name)
    scenario.initial_scenario_record_path = f"{ADS_SCENARIO_DIR}/{record_name}.yaml"
    scenario.extract_map_name()

    file_name_list = os.listdir(f"{ADS_RECORDS_DIR}/{scenario.record_name}")
    for file_name in file_name_list:
        if ".xosc" not in file_name:
            scenario.record_dir = f"{ADS_RECORDS_DIR}/{scenario.record_name}/{file_name}"
            scenario.record_root_path = f"{ADS_RECORDS_DIR}/{scenario.record_name}"
    scenario.violation_results = scenario.measure_violations()

    print(f"Violations: {scenario.violation_results}")
    decision_count = analyze_decision(f"/home/cloudsky/autoware/records/{record_name}/{record_name}_0")
    print(f"Decision count: {decision_count}")
    sinuosity = analyze_sinuosity(f"/home/cloudsky/autoware/records/{record_name}/{record_name}_0")
    print(f"Sinuosity: {sinuosity}")