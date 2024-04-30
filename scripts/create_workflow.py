import yaml
import sys
from pathlib import Path


def create_workflow(directory_path, output_path):

    scenarios = list(Path(directory_path).glob('*.yaml'))

    scenarios.sort()
    data = {'Scenario': [{'path': str(path.resolve())} for path in scenarios]}

    with open(output_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)
    print(f"YAML file '{output_path}' has been generated successfully.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python create_workflow.py <directory_path> <output_path>")
        sys.exit(1)
    directory_path = sys.argv[1]
    output_path = sys.argv[2]
    create_workflow(directory_path, output_path)
