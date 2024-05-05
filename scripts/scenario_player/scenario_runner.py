import os
import glob
import docker
from container_manager import ContainerManager

if __name__ == '__main__':
    ADS_ROOT = "/home/sora/Desktop/changnam"
    EXP_ROOT = "/home/sora/Desktop/changnam/experiments"
    MAP_PATH = ADS_ROOT + "/autoware_map"
    DOCKER_CONTAINER_NAME = "transformer"
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
    container_id = 45163
    for scenario_path in scenario_paths:

        container_manager.start_instance(
            container_id=f"{container_id}",
            container_name=f"{DOCKER_CONTAINER_NAME}_{container_id}",
            map_path=MAP_PATH,
            scenario_path=SCENARIO_DIR,
            script_path=SCRIPT_DIR,
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
