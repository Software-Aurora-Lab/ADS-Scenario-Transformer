import sys
import os
import subprocess
from pathlib import Path
import json


def file_has_extension(filename, extension):
    file_path = Path(filename)
    return file_path.suffix == '.' + extension


def run_scenario_transformer(directory_path, config_path):
    """
    Transform all scenarios in given directory
    """

    with open(config_path, 'r') as file:
        config = json.load(file)

    for filename in os.listdir(directory_path):
        full_file_path = os.path.join(directory_path, filename)

        if file_has_extension(full_file_path, "00000"):
            command = [
                'poetry', 'run', 'python', '-m',
                'ads_scenario_transformer.__main__', '--apollo-map-path',
                config["apollo-map-path"], '--vector-map-path',
                config["vector-map-path"], '--apollo-scenario-path',
                full_file_path, '--road-network-lanelet-map-path',
                config["road-network-lanelet-map-path"], '--source-name',
                config["source-name"], '--obstacle-waypoint-frequency',
                str(config["obstacle-waypoint-frequency"]),
                '--output-scenario-path', config["output-scenario-path"]
            ]

            if config["disable-traffic-signal"]:
                command.append('--disable-traffic-signal')

            if config["use-last-position-destination"]:
                command.append('--use-last-position-destination')

            print("Executing command:", ' '.join(command))

            # Execute the command
            result = subprocess.run(command, capture_output=True, text=True)
            if result.stdout:
                print("Output:", result.stdout)
            if result.stderr:
                print("Error:", result.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python run_scenarios.py <directory_path> <json_config_path>"
        )
        sys.exit(1)
    directory_path = sys.argv[1]
    config_path = sys.argv[2]
    run_scenario_transformer(directory_path, config_path)
