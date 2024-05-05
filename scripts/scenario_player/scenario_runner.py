import os
import glob
import docker
import random
import csv
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


def create_result_data(result_file_path) -> List[CSVResult]:
    tree = ET.parse(result_file_path)
    root = tree.getroot()
    results = []
    for testsuite in root.findall('testsuite'):
        for testcase in testsuite.findall('testcase'):
            error = testcase.find('error')
            if error is not None:
                results.append(
                    CSVResult(scenario_name=testcase.attrib['name'],
                              is_success=False,
                              error_type=error.attrib['type'],
                              message=error.attrib['message']))
            else:
                results.append(
                    CSVResult(scenario_name=testcase.attrib['name'],
                              is_success=True,
                              error_type=None,
                              message=None))
    return results


def write_result_to_csv(result, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ['Scenario Name', 'P/F', 'Error Type', 'Error Message'])

        for result in result:
            writer.writerow([
                result.scenario_name, result.is_success, result.error_type,
                result.message
            ])


if __name__ == '__main__':
    ADS_ROOT = "/home/sora/Desktop/changnam"
    EXP_ROOT = "/home/sora/Desktop/changnam/experiments"
    MAP_PATH = ADS_ROOT + "/autoware_map"
    DOCKER_CONTAINER_NAME = "ads_scenario_transformer"
    DOCKER_IMAGE_ID = "6f0050135292"
    EXP_NO = 1

    SINGLE_EXP_ROOT = EXP_ROOT + f"/exp-{EXP_NO}"
    SCRIPT_DIR = SINGLE_EXP_ROOT + "/scripts"
    SCENARIO_DIR = SINGLE_EXP_ROOT + "/scenarios"
    LOG_DIR = SINGLE_EXP_ROOT + "/log"

    os.makedirs(SCRIPT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    container_manager = ContainerManager(ads_root=ADS_ROOT)

    pattern = f"{SCENARIO_DIR}/borregas/*.yaml"
    scenario_paths = glob.glob(pattern, recursive=True)

    print("scenario_paths:", scenario_paths)
    container_id = random.randint(100, 100000)

    csv_results = []
    for scenario_path in scenario_paths:

        container_manager.start_instance(
            container_id=f"{container_id}",
            container_name=f"{DOCKER_CONTAINER_NAME}_{container_id}",
            map_path=MAP_PATH,
            scenario_path=SCENARIO_DIR,
            script_path=SCRIPT_DIR,
            log_path=LOG_DIR,
            docker_image_id=DOCKER_IMAGE_ID)

        running_script_path = container_manager.create_scenario_running_script(
            container_id=f"{container_id}",
            script_dir=SCRIPT_DIR,
            scenario_file_path=scenario_path,
            log_dir_path=LOG_DIR)

        print(
            "exec:",
            container_manager.execute_script_in_container(running_script_path))
        container_manager.remove_instance()
        container_id += 1

        results = create_result_data(result_file_path=LOG_DIR +
                                     "/scenario_test_runner/result.junit.xml")
        csv_results.extend(results)

    write_result_to_csv(result=csv_results,
                        filename=SINGLE_EXP_ROOT + "summary.csv")
