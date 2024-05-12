import time
import subprocess
from threading import Thread
from src.config import MAX_RECORD_TIME, MY_SCRIPTS_DIR, AUTOWARE_CMD_PREPARE_TIME, ADS_RECORDS_DIR, TMP_RECORDS_DIR

def replay_scenarios_in_threading(scenario_list, containers):
    sub_scenario_list_list = [scenario_list[x:x + len(containers)] for x in
                              range(0, len(scenario_list), len(containers))]
    for sub_scenario_list in sub_scenario_list_list:
        thread_list = []
        for scenario, container in zip(sub_scenario_list, containers):
            t_replay = Thread(target=replay_scenario, args=(scenario, container,))
            thread_list.append(t_replay)
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
        # time.sleep(1)


def replay_scenario(scenario, container):
    container.kill_process()
    start_replay(scenario, container)
    move_scenario_record_dir(scenario, container)
    scenario.update_scenario_record_dir_info()


def move_scenario_record_dir(scenario, container):
    cmd = f"docker exec {container.container_name} mv {TMP_RECORDS_DIR}/{scenario.record_name} {ADS_RECORDS_DIR}/{scenario.record_name}"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    p.wait()


def start_replay(scenario, container):
    script_path = container.scenario_script_update(scenario)
    cmd = f"docker exec --env-file {MY_SCRIPTS_DIR}/{container.env_file} {container.container_name} /bin/bash {script_path}"
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time_start = time.time()
    while p.poll() is None:
        if MAX_RECORD_TIME + AUTOWARE_CMD_PREPARE_TIME < time.time() - time_start:
            container.stop_recorder()
            break
    time.sleep(0.5)
    container.kill_process()
    p.wait()
