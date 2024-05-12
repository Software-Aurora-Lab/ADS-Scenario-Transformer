import os
import subprocess
import ruamel.yaml
from src.config import ADS_RECORDS_DIR, ADS_TEMP_SCENARIO_DIR
from environment.MapLoader import MapLoader
from src.tools.file_handling import delete_dir
from src.objectives.violation_number.oracles import RecordAnalyzer
from src.objectives.violation_number.oracles.impl.ComfortOracle import ComfortOracle
from src.objectives.violation_number.oracles.impl.SpeedingOracle import SpeedingOracle
from src.objectives.violation_number.oracles.impl.CollisionOracle import CollisionOracle
from src.objectives.violation_number.oracles.impl.JunctionLaneChangeOracle import JunctionLaneChangeOracle
from src.objectives.violation_number.oracles.impl.ModuleDelayOracle import ModuleDelayOracle
from src.objectives.violation_number.oracles.impl.ModuleOracle import ModuleOracle
from src.objectives.violation_number.oracles.impl.UnsafeLaneChangeOracle import UnsafeLaneChangeOracle


class Scenario:
    def __init__(self, record_name):
        self.has_emerged_violations = False
        self.has_emerged_module_violations = False
        self.record_name = record_name
        self.record_dir = ""
        self.record_root_path = ""
        self.duration = 0
        self.analysis_time = 0

    def update_record_id(self, record_id):
        self.record_id = record_id

    def update_record_name(self, new_record_name):
        self.record_name = new_record_name

    def copy_temp_scenario_file(self):
        previous_initial_scenario_record_path = self.initial_scenario_record_path
        self.initial_scenario_record_path = f"{ADS_TEMP_SCENARIO_DIR}/{self.record_name}.yaml"
        cmd = f"cp -rf {previous_initial_scenario_record_path} {self.initial_scenario_record_path}"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.wait()

    def delete_scenario_file(self):
        cmd = f"rm -rf {self.initial_scenario_record_path}"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.wait()

    def measure_violations(self):
        MapLoader(self.map_name)

        # violations = []
        target_oracles = [
            ComfortOracle(),
            CollisionOracle(),
            SpeedingOracle(),
            ModuleDelayOracle(),
            ModuleOracle(),
            UnsafeLaneChangeOracle(),
            JunctionLaneChangeOracle()
        ]

        analyzer = RecordAnalyzer(record_path=str(self.record_dir), oracles=target_oracles)
        violations = analyzer.analyze()
        print(f"        {self.record_name}: {[(violation.main_type, violation.key_label) for violation in violations]}")
        return violations

    def update_emerged_status(self, violations_emerged_results, contain_module_violation):
        if len(violations_emerged_results) > 0:
            self.has_emerged_violations = True
            if contain_module_violation:
                self.has_emerged_module_violations = True

    def delete_record(self):
        delete_dir(self.record_root_path, False)

    def update_config_file_status(self, config_file_status):
        self.config_file_status = config_file_status

    def update_original_violations(self, pre_record_info):
        self.original_violation_num = pre_record_info.violation_num
        self.original_violation_results = pre_record_info.violation_results

    def update_record_info(self, pre_record_info):
        self.update_original_violations(pre_record_info)
        self.initial_scenario_record_path = pre_record_info.record_file_path
        self.initial_scenario_record_name = pre_record_info.record_name
        self.map_name = pre_record_info.map_name

    def update_scenario_record_dir_info(self):
        file_name_list = os.listdir(f"{ADS_RECORDS_DIR}/{self.record_name}")
        for file_name in file_name_list:
            if ".xosc" not in file_name:
                self.record_dir = f"{ADS_RECORDS_DIR}/{self.record_name}/{file_name}"
                self.record_root_path = f"{ADS_RECORDS_DIR}/{self.record_name}"

    def extract_map_name(self):
        ruamel_yaml = ruamel.yaml.YAML()
        with open(self.initial_scenario_record_path, "r") as read_file:
            ruamel_yaml_scenario_file = ruamel_yaml.load(read_file)
        logic_file_path = ruamel_yaml_scenario_file['OpenSCENARIO']['RoadNetwork']['LogicFile']['filepath']
        lanelet_map_name = logic_file_path.split('/')[-2]
        self.map_name = lanelet_map_name
