import sys
import os
import subprocess
from pathlib import Path
import json
import pprint
from ads_scenario_transformer.transformer.scenario_transformer import ScenarioTransformer, ScenarioTransformerConfiguration
from ads_scenario_transformer.openscenario.openscenario_coder import OpenScenarioEncoder


def file_has_extension(filename, extension):
    file_path = Path(filename)
    return file_path.suffix == '.' + extension


def run_scenario_transformer(directory_path, config_path):
    """
    Transform all scenarios in given directory
    """

    with open(config_path, 'r') as file:
        config = json.load(file)

    for filename in sorted(os.listdir(directory_path)):
        full_file_path = os.path.join(directory_path, filename)

        if file_has_extension(full_file_path, "00000"):

            configuration = ScenarioTransformerConfiguration(
                apollo_scenario_path=full_file_path,
                apollo_hd_map_path=config["apollo-map-path"],
                vector_map_path=config["vector-map-path"],
                road_network_lanelet_map_path=config[
                    "road-network-lanelet-map-path"],
                road_network_pcd_map_path="point_cloud.pcd",
                obstacle_direction_change_detection_threshold=0,
                obstacle_waypoint_frequency_in_sec=config[
                    "obstacle-waypoint-frequency"],
                disable_traffic_signal=config["disable-traffic-signal"],
                use_last_position_as_destination=config[
                    "use-last-position-destination"])

            transformer = ScenarioTransformer(configuration=configuration)
            scenario = transformer.transform()
            scenario_yaml = OpenScenarioEncoder.encode_proto_pyobject_to_yaml(
                proto_pyobject=scenario, wrap_result_with_typename=False)

            filename = ""
            if config["source-name"]:
                filename = config["source-name"]
                filename = filename + "-" + Path(full_file_path).stem
            else:
                filename = Path(full_file_path).stem

            output_path = Path(
                config["output-scenario-path"]) / (filename + ".yaml")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            print("Configuration")
            pprint.pprint(vars(configuration), indent=4)
            print(f"File will saved at {output_path}")
            with open(output_path, 'w') as file:
                file.write(scenario_yaml)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python run_scenarios.py <directory_path> <json_config_path>"
        )
        sys.exit(1)
    directory_path = sys.argv[1]
    config_path = sys.argv[2]
    run_scenario_transformer(directory_path, config_path)
