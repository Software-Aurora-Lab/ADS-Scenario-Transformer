import sys
import csv
import shutil
from typing import List, Dict, Tuple
from pathlib import Path
from dataclasses import dataclass
from src.objectives.violation_number.oracles import RecordAnalyzer, Violation
from src.objectives.violation_number.oracles.impl.ComfortOracle import ComfortOracle
from src.objectives.violation_number.oracles.impl.SpeedingOracle import SpeedingOracle
from src.objectives.violation_number.oracles.impl.CollisionOracle import CollisionOracle
from src.objectives.violation_number.oracles.impl.JunctionLaneChangeOracle import JunctionLaneChangeOracle
from src.objectives.violation_number.oracles.impl.ModuleDelayOracle import ModuleDelayOracle
from src.objectives.violation_number.oracles.impl.ModuleOracle import ModuleOracle
from src.objectives.violation_number.oracles.impl.UnsafeLaneChangeOracle import UnsafeLaneChangeOracle
from src.environment.MapLoader import MapLoader


class ViolationAnalyzer:
    """
    Violation Anlayzer analyzes record of Autoware and provide violation information.
    It must be run on Autoware enabled environment.
    """

    def __init__(self, record_dir):
        self.record_dir = record_dir
        self.target_oracles = [
            ComfortOracle(),
            CollisionOracle(),
            SpeedingOracle(),
            ModuleDelayOracle(),
            ModuleOracle(),
            UnsafeLaneChangeOracle(),
            JunctionLaneChangeOracle()
        ]

        self.analyzer = RecordAnalyzer(record_path=str(self.record_dir),
                                       oracles=self.target_oracles)

    @property
    def record_name(self) -> str:
        return Path(self.record_dir).stem

    def analyze(self) -> Violation:
        violations = self.analyzer.analyze()
        print(
            f"{self.record_name}: {[(violation.main_type, violation.key_label) for violation in violations]}"
        )
        return violations


def write_result_to_csv(scenario_name, violations, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['scenario_name', 'main_type', 'features', 'key_label']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for violation in violations:
            writer.writerow({
                'scenario_name': scenario_name,
                'main_type': str(violation.main_type),
                'features': str(violation.features),
                'key_label': violation.key_label
            })


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python violation_analyzer.py <record_directory_path> <output_directory_path> <map_path>"
        )
        sys.exit(1)

    record_directory_path = sys.argv[1]
    output_directory_path = sys.argv[2]

    map_loader = MapLoader(sys.argv[3])

    analyzer = ViolationAnalyzer(record_dir=record_directory_path)
    violations = analyzer.analyze()
    print(violations)
    write_result_to_csv(
        scenario_name=analyzer.record_name,
        violations=violations,
        filename=f"{output_directory_path}/violation_{analyzer.record_name}.csv"
    )
    shutil.rmtree(record_directory_path)
