import sys
import os
import csv
from pathlib import Path
from dataclasses import dataclass
import json
import pprint
from ads_scenario_transformer.transformer.scenario_transformer import ScenarioTransformer, ScenarioTransformerConfiguration
from ads_scenario_transformer.openscenario.openscenario_coder import OpenScenarioEncoder


@dataclass
class CSVResult:
    file_path: str
    message: str
    configuration: str


def write_result(result, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["File Path", 'Message', 'Configuration'])

        for result in result:
            writer.writerow(
                [result.file_path, result.message, result.configuration])
        print("Write a summary at:", {filename})


def file_has_extension(filename, extension):
    file_path = Path(filename)
    return file_path.suffix == '.' + extension


def run_scenario_transformer(directory_path, config_path):
    """
    Transform all scenarios in given directory
    """

    with open(config_path, 'r') as file:
        config = json.load(file)

    results = []
    configuration = ""
    output_dir_path = ""
    for i, filename in sorted(enumerate(os.listdir(directory_path))):
        full_file_path = os.path.join(directory_path, filename)

        if file_has_extension(full_file_path, "00000"):
            try:
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
                        "use-last-position-destination"],
                    add_violation_detecting_conditions=config[
                        "add-violation-detecting-conditions"])

                transformer = ScenarioTransformer(configuration=configuration)
                scenario = transformer.transform()
                scenario_yaml = OpenScenarioEncoder.encode_proto_pyobject_to_yaml(
                    proto_pyobject=scenario, wrap_result_with_typename=False)

                filename = f"{i}_"
                if config["source-name"]:
                    filename = filename + config["source-name"]
                    filename = filename + "-" + Path(full_file_path).stem
                else:
                    filename = filename + Path(full_file_path).stem

                output_path = Path(
                    config["output-scenario-path"]) / (filename + ".yaml")
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_dir_path = output_path.parent

                print("Configuration")
                pprint.pprint(vars(configuration), indent=4)
                print(f"File will saved at {output_path}")

                results.append(
                    CSVResult(file_path=str(output_path),
                              message="Success",
                              configuration=str(configuration)))
                with open(output_path, 'w') as file:
                    file.write(scenario_yaml)
            except Exception as ex:
                print(f"Error while transforming {full_file_path}, {ex}")
                results.append(
                    CSVResult(file_path=full_file_path,
                              message=str(ex),
                              configuration=str(configuration)))

    write_result(
        result=results,
        filename=f"{output_dir_path.absolute()}/transformation_summary.csv")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python run_scenarios.py <directory_path> <json_config_path>"
        )
        sys.exit(1)
    directory_path = sys.argv[1]
    config_path = sys.argv[2]
    run_scenario_transformer(directory_path, config_path)
