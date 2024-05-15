import os
import shutil
import random
import csv
import argparse
import subprocess
import yaml
from pathlib import Path
from typing import List, Optional
from enum import Enum
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from scripts.scenario_player.container_manager import ContainerManager


class CSVWorker:

    @staticmethod
    def write_scenario_result(result, filename):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Scenario Name', 'Source', 'S/F/E', 'Error Type',
                'Error Message', "File Path"
            ])

            for result in result:
                source = "DoppelTest" if result.scenario_name in "Doppel" else "scenoRITA"
                writer.writerow([
                    result.scenario_name, source, result.result_type.value,
                    result.error_type, result.message, result.file_path
                ])
            print("Write a summary at:", {filename})

    @staticmethod
    def write_violation_result(scenario_name, violations, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'scenario_name', 'main_type', 'features', 'key_label'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for violation in violations:
                writer.writerow({
                    'scenario_name': scenario_name,
                    'main_type': str(violation.main_type),
                    'features': str(violation.features),
                    'key_label': violation.key_label
                })

    @staticmethod
    def merge_violation_results(directory_path: str, output_path: str):
        violation_files = [
            entry.resolve()
            for entry in Path(directory_path).rglob('violation*.csv')
        ]
        violations = []

        for violation_file in violation_files:
            with open(violation_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    violations.append(row)

        with open(output_path, 'w', newline='') as merged_file:
            fieldnames = violations[0].keys()
            writer = csv.DictWriter(merged_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(violations)


class ResultType(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


@dataclass
class CSVResult:
    scenario_name: str
    result_type: ResultType
    error_type: Optional[str]
    message: Optional[str]
    file_path: str


@dataclass
class ExperimentConfiguration:

    def __init__(self, ads_root: str, project_root: str, experiment_id: int,
                 docker_image_id: str, display_gui: bool,
                 analyze_scenario: bool):
        self.ads_root = ads_root
        self.project_root = project_root
        self.experiment_id = experiment_id
        self.docker_image_id = docker_image_id
        self.display_gui = display_gui
        self.analyze_scenario = analyze_scenario

        self.cached_map_path = {}

    @property
    def exp_root(self):
        return f"{self.ads_root}/experiments"

    @property
    def map_path(self):
        return f"{self.ads_root}/autoware_map"

    @property
    def docker_container_name(self):
        return "ads_scenario_transformer"

    @property
    def single_exp_root(self):
        return f"{self.exp_root}/exp_{self.experiment_id}"

    @property
    def script_dir(self):
        return f"{self.single_exp_root}/scripts"

    @property
    def scenario_dir(self):
        return f"{self.single_exp_root}/scenarios"

    @property
    def log_dir(self):
        return f"{self.single_exp_root}/log"

    @property
    def finished_scenario_dir(self):
        return f"{self.single_exp_root}/fin_scenarios"

    @property
    def confVE_path(self):
        return f"{self.project_root}/pkgs/ConfVE_Autoware"

    @property
    def violation_analyzer_path(self):
        return f"{self.confVE_path}/violation_analyzer.py"

    def rosbag_record_path(self, scenario_name: str) -> str:
        return f"{self.log_dir}/scenario_test_runner/{scenario_name}/{scenario_name}"

    def target_map_path(self, scenario_path: str, cache_no: int) -> str:
        if cache_no in self.cached_map_path:
            return self.cached_map_path[cache_no]

        with open(scenario_path, 'r') as file:
            yaml_contents = yaml.load(file, Loader=yaml.FullLoader)

        scenario_map_path = yaml_contents['OpenSCENARIO']['RoadNetwork'][
            'LogicFile']['filepath']

        self.cached_map_path[cache_no] = self.map_path + "/" + "/".join(
            Path(scenario_map_path).parts[-2:])
        return self.cached_map_path[cache_no]


class ExperimentRunner:
    configuration: ExperimentConfiguration

    def __init__(self, configuration: ExperimentConfiguration):
        self.configuration = configuration
        os.makedirs(self.configuration.script_dir, exist_ok=True)
        os.makedirs(self.configuration.log_dir, exist_ok=True)
        os.makedirs(self.configuration.finished_scenario_dir, exist_ok=True)

        self.container_manager = ContainerManager(
            ads_root=self.configuration.ads_root)
        self.container_id = random.randint(100, 100000)
        self.container_name = f"{self.configuration.docker_container_name}_{self.container_id}"
        self.recording_process = None
        self.all_results = []
        self.replayed = False

    @property
    def scenario_paths(self):
        scenario_directories = Path(self.configuration.scenario_dir)
        scenario_dict = {}
        for scenario_dir in scenario_directories.iterdir():
            yaml_files = [
                entry.resolve() for entry in scenario_dir.glob('*.yaml')
            ]
            yml_files = [
                entry.resolve() for entry in scenario_dir.glob('*.yml')
            ]
            scenario_dict[scenario_dir] = sorted(yaml_files + yml_files)

        return scenario_dict

    def run_experiment(self, enable_display_recording: bool):
        print("Running Scenarios:", self.scenario_paths.values())
        map_count = len(self.scenario_paths)

        exp_results = []
        for idx, (scenario_dir,
                  scenario_paths) in enumerate(self.scenario_paths.items()):

            scenario_count = len(scenario_paths)
            scenario_dir_name = Path(scenario_dir).stem
            csv_results = []
            for scenario_idx, scenario in enumerate(scenario_paths):
                scenario_name = Path(scenario).stem

                if enable_display_recording:
                    print("Start Recording:", scenario_name)
                    output_file = f'{self.configuration.log_dir}/{scenario_name}.mp4'
                    self.recording_process = self.start_recording(output_file)

                self.container_manager.start_instance(
                    container_id=f"{self.container_id}",
                    container_name=self.container_name,
                    map_path=self.configuration.map_path,
                    scenario_path=self.configuration.scenario_dir,
                    script_path=self.configuration.script_dir,
                    log_path=self.configuration.log_dir,
                    project_path=self.configuration.project_root,
                    docker_image_id=self.configuration.docker_image_id,
                    display_gui=self.configuration.display_gui)

                env_setup_path = self.container_manager.create_env_setup_script(
                    container_id=f"{self.container_id}",
                    script_dir=self.configuration.script_dir,
                    confVE_path=self.configuration.confVE_path)
                print(
                    "exec env setup:",
                    self.container_manager.execute_script_in_container(
                        env_setup_path))

                running_script_path = self.container_manager.create_scenario_running_script(
                    container_id=f"{self.container_id}",
                    script_dir=self.configuration.script_dir,
                    scenario_file_path=scenario,
                    log_dir_path=self.configuration.log_dir,
                    record=self.configuration.analyze_scenario,
                    confVE_path=self.configuration.confVE_path)

                print(
                    "exec scenario running:",
                    self.container_manager.execute_script_in_container(
                        running_script_path))

                if enable_display_recording:
                    if self.recording_process:
                        print("Stop Recording:", scenario_name)
                        self.stop_recording(self.recording_process)

                if self.configuration.analyze_scenario:
                    print("Start Analyzing:", scenario_name)
                    analyzing_script_path = self.container_manager.create_scenario_analyzing_script(
                        container_id=f"{self.container_id}",
                        script_dir=self.configuration.script_dir,
                        record_path=self.configuration.rosbag_record_path(
                            scenario_name=scenario_name),
                        log_dir_path=self.configuration.log_dir,
                        confVE_path=self.configuration.confVE_path,
                        violation_analyzer_path=self.configuration.
                        violation_analyzer_path,
                        map_path=self.configuration.target_map_path(
                            scenario_path=scenario, cache_no=idx))

                    print(
                        "exec:",
                        self.container_manager.execute_script_in_container(
                            analyzing_script_path))

                self.container_manager.remove_instance()
                self.container_id += 1
                scenario_result_path = self.configuration.log_dir + "/scenario_test_runner/result.junit.xml"

                finished_scneario_path = self.move_finished_scenario(
                    scenario_path=scenario,
                    scenario_name=scenario_name,
                    scenario_dir_name=scenario_dir_name)
                results = self.create_result_data(
                    result_file_path=scenario_result_path,
                    scneario_path=finished_scneario_path)
                csv_results.extend(results)
                self.create_intermediate_result(csv_results,
                                                scenario_result_path,
                                                scenario_name)

                print(f"{scenario_idx + 1}/{scenario_count} done")

            CSVWorker.write_scenario_result(
                result=csv_results,
                filename=self.summary_path(scenario_dir_name))

            pass_count = len([
                result for result in csv_results
                if result.result_type == ResultType.SUCCESS
            ])
            print(
                f"Finished {scenario_dir}. Pass {pass_count} out of {len(csv_results)}. Progress: {idx + 1}/{map_count}"
            )
            exp_results.extend(csv_results)

        if self.replayed:
            self.update_replayed_results(exp_results=exp_results)

            CSVWorker.write_scenario_result(
                self.all_results, filename=self.summary_path(name=None))

            if self.configuration.analyze_scenario:
                CSVWorker.merge_violation_results(
                    directory_path=self.configuration.log_dir,
                    output_path=self.configuration.single_exp_root +
                    "/violations.csv")
        else:
            self.all_results.extend(exp_results)
            self.replay_autoware_failed_scenarios(exp_results)

    def update_replayed_results(self, exp_results: List[CSVResult]):
        filtered_results = []
        for old_result in self.all_results:
            for new_result in exp_results[:]:
                if old_result.scenario_name == new_result.scenario_name:
                    filtered_results.append(new_result)
                    exp_results.remove(new_result)
                    break
            else:
                filtered_results.append(old_result)
                
        filtered_results.extend(exp_results)
        self.all_results = filtered_results

    def replay_autoware_failed_scenarios(self, all_results: List[CSVResult]):
        if os.path.exists(self.configuration.scenario_dir):
            shutil.rmtree(self.configuration.scenario_dir)
            os.makedirs(self.configuration.scenario_dir)

        autoware_failed_scenario_names = [
            result.scenario_name for result in all_results
            if result.error_type and result.error_type.startswith("Autoware")
        ]

        scenario_replay_dir = self.configuration.scenario_dir + "/replay_errors"
        if not os.path.exists(scenario_replay_dir):
            os.makedirs(scenario_replay_dir)

        for scenario_name in autoware_failed_scenario_names:
            yaml_files = [
                entry.resolve()
                for entry in Path(self.configuration.finished_scenario_dir).
                rglob(f'{scenario_name}.yaml')
            ]
            if yaml_files:
                from_path = yaml_files[0]
                to_path = scenario_replay_dir + f"/{scenario_name}.yaml"
                shutil.move(from_path, to_path)

        self.replayed = True
        self.run_experiment(enable_display_recording=False)

    def move_finished_scenario(self, scenario_path: str, scenario_name: str,
                               scenario_dir_name: str) -> str:
        map_path = self.configuration.finished_scenario_dir + f"/{scenario_dir_name}"
        output_path = f"{map_path}/{scenario_name}.yaml"

        if not os.path.exists(map_path):
            os.makedirs(map_path)

        shutil.move(scenario_path, output_path)
        return output_path

    def summary_path(self, name: Optional[str]) -> str:
        if name:
            return self.configuration.single_exp_root + f"/exp_{self.configuration.experiment_id}_{name}_summary.csv"
        else:
            return self.configuration.single_exp_root + f"/exp_{self.configuration.experiment_id}_all_summary.csv"

    def create_intermediate_result(self, results, scenario_result_path,
                                   scenario_name):
        shutil.copy(
            scenario_result_path,
            self.configuration.log_dir + f"/result_{scenario_name}.junit.xml")

        CSVWorker.write_scenario_result(result=results,
                                        filename=self.configuration.log_dir +
                                        "/intermediate_summary.csv")

    def create_result_data(self, result_file_path: str,
                           scneario_path: str) -> List[CSVResult]:
        tree = ET.parse(result_file_path)
        root = tree.getroot()
        results = []
        for testsuite in root.findall('testsuite'):
            for testcase in testsuite.findall('testcase'):
                error = testcase.find('error')
                failure = testcase.find('failure')
                if error is not None:
                    results.append(
                        CSVResult(scenario_name=testcase.attrib['name'],
                                  result_type=ResultType.ERROR,
                                  error_type=error.attrib['type'],
                                  message=error.attrib['message'],
                                  file_path=scneario_path))
                elif failure is not None:
                    results.append(
                        CSVResult(scenario_name=testcase.attrib['name'],
                                  result_type=ResultType.FAILURE,
                                  error_type=failure.get('type'),
                                  message=failure.get('message'),
                                  file_path=scneario_path))
                else:
                    results.append(
                        CSVResult(scenario_name=testcase.attrib['name'],
                                  result_type=ResultType.SUCCESS,
                                  error_type=None,
                                  message=None,
                                  file_path=scneario_path))
        return results

    def start_recording(self,
                        output_filename,
                        display_number=':0',
                        screen_number='0',
                        resolution='1920x1080'):
        command = [
            'ffmpeg', '-video_size', resolution, '-framerate', '25', '-f',
            'x11grab', '-i', f'{display_number}.{screen_number}', '-vf',
            'format=yuv420p', output_filename
        ]
        process = subprocess.Popen(command)
        return process

    def stop_recording(self, process):
        process.terminate()
        process.wait()


if __name__ == '__main__':

    ADS_ROOT = "/home/sora/Desktop/changnam"
    PROJECT_ROOT = "/home/sora/Desktop/changnam/ADS-scenario-transfer"
    DOCKER_IMAGE_ID = "6f0050135292"

    parser = argparse.ArgumentParser(description="Process the experiment ID.")
    parser.add_argument('--experiment_id',
                        type=int,
                        default=1,
                        help='An integer for the experiment ID')

    args = parser.parse_args()
    EXPERIMENT_ID = args.experiment_id

    os.system("xhost +local:docker")
    runner = ExperimentRunner(
        configuration=ExperimentConfiguration(ads_root=ADS_ROOT,
                                              project_root=PROJECT_ROOT,
                                              experiment_id=EXPERIMENT_ID,
                                              docker_image_id=DOCKER_IMAGE_ID,
                                              display_gui=False,
                                              analyze_scenario=False))

    runner.run_experiment(enable_display_recording=False)
