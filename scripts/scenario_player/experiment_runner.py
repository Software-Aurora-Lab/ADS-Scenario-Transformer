import os
import shutil
import random
import csv
import argparse
import subprocess
import threading
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from container_manager import ContainerManager


@dataclass
class CSVResult:
    scenario_name: str
    is_success: bool
    error_type: Optional[str]
    message: Optional[str]


@dataclass
class ExperimentConfiguration:

    def __init__(self, ads_root: str, experiment_id: int, docker_image_id: str,
                 container_timeout_sec: float):
        self.ads_root = ads_root
        self.experiment_id = experiment_id
        self.docker_image_id = docker_image_id
        self.container_timeout_sec = container_timeout_sec

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

    @property
    def scenario_paths(self):
        map_directories = Path(self.configuration.scenario_dir)
        scenario_dict = {}
        for map_dir in map_directories.iterdir():
            yaml_files = [entry.resolve() for entry in map_dir.glob('*.yaml')]
            yml_files = [entry.resolve() for entry in map_dir.glob('*.yml')]
            scenario_dict[map_dir] = sorted(yaml_files + yml_files)

        return scenario_dict

    def run_experiment(self, enable_recording: bool):
        print("Running Scenarios:", self.scenario_paths.values())
        map_count = len(self.scenario_paths)

        all_results = []
        for idx, (map_dir,
                  scenario_paths) in enumerate(self.scenario_paths.items()):

            scenario_count = len(scenario_paths)
            map_name = Path(map_dir).stem
            csv_results = []
            for scenario_idx, scenario in enumerate(scenario_paths):
                scenario_name = Path(scenario).stem

                if enable_recording:
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
                    docker_image_id=self.configuration.docker_image_id)

                running_script_path = self.container_manager.create_scenario_running_script(
                    container_id=f"{self.container_id}",
                    script_dir=self.configuration.script_dir,
                    scenario_file_path=scenario,
                    log_dir_path=self.configuration.log_dir,
                    launch_rviz=True)

                print(
                    "exec:",
                    self.container_manager.execute_script_in_container(
                        running_script_path))

                if enable_recording:
                    if self.recording_process:
                        print("Stop Recording:", scenario_name)
                        self.stop_recording(self.recording_process)

                self.container_manager.remove_instance()
                self.container_id += 1
                scenario_result_path = self.configuration.log_dir + "/scenario_test_runner/result.junit.xml"
                results = self.create_result_data(
                    result_file_path=scenario_result_path)
                csv_results.extend(results)
                self.create_intermediate_result(csv_results,
                                                scenario_result_path,
                                                scenario_name)

                self.move_finished_scenario(scenario_path=scenario,
                                            scenario_name=scenario_name,
                                            map_name=map_name)

                print(f"{scenario_idx + 1}/{scenario_count} done")

            self.write_result_to_csv(result=csv_results,
                                     filename=self.summary_path(map_name))

            pass_count = len(
                [result for result in csv_results if result.is_success])
            print(
                f"Finished {map_name}. Pass {pass_count} out of {len(csv_results)}. Progress: {idx + 1}/{map_count}"
            )
            all_results.extend(csv_results)

        self.write_result_to_csv(result=all_results,
                                 filename=self.summary_path(map_name=None))

        self.replay_autoware_failed_scenarios(all_results)

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
            from_path = self.configuration.finished_scenario_dir + f"/{scenario_name}.yaml"
            to_path = scenario_replay_dir + f"/{scenario_name}.yaml"
            shutil.move(from_path, to_path)

        self.run_experiment(enable_recording=False)

    def move_finished_scenario(self, scenario_path: str, scenario_name: str,
                               map_name: str):
        map_path = self.configuration.finished_scenario_dir + f"/{map_name}"
        output_path = f"{map_path}/{scenario_name}.yaml"

        if not os.path.exists(map_path):
            os.makedirs(map_path)

        shutil.move(scenario_path, output_path)

    def summary_path(self, map_name: Optional[str]) -> str:
        if map_name:
            return self.configuration.single_exp_root + f"/exp_{self.configuration.experiment_id}_{map_name}_summary.csv"
        else:
            return self.configuration.single_exp_root + f"/exp_{self.configuration.experiment_id}_all_summary.csv"

    def create_intermediate_result(self, results, scenario_result_path,
                                   scenario_name):

        shutil.copy(
            scenario_result_path,
            self.configuration.log_dir + f"/result_{scenario_name}.junit.xml")

        self.write_result_to_csv(result=results,
                                 filename=self.configuration.log_dir +
                                 f"/intermediate_summary.csv")

    def create_result_data(self, result_file_path) -> List[CSVResult]:
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
                                  is_success=False,
                                  error_type=error.attrib['type'],
                                  message=error.attrib['message']))
                elif failure is not None:
                    results.append(
                        CSVResult(scenario_name=testcase.attrib['name'],
                                  is_success=False,
                                  error_type=failure.get('type'),
                                  message=failure.get('message')))
                else:
                    results.append(
                        CSVResult(scenario_name=testcase.attrib['name'],
                                  is_success=True,
                                  error_type=None,
                                  message=None))
        return results

    def write_result_to_csv(self, result, filename):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                ['Scenario Name', 'P/F', 'Error Type', 'Error Message'])

            for result in result:
                writer.writerow([
                    result.scenario_name, result.is_success, result.error_type,
                    result.message
                ])
            print("Write a summary at:", {filename})

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
                                              experiment_id=EXPERIMENT_ID,
                                              docker_image_id=DOCKER_IMAGE_ID,
                                              container_timeout_sec=120))

    runner.run_experiment(enable_recording=False)
