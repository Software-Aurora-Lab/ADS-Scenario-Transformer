import os
from src.config import (MY_SCRIPTS_DIR, DIR_ROOT, ADS_ROOT, PRE_SCRIPTS_DIR, PROJECT_ROOT,
                    AUTOWARE_CURRENT_MODULE_CONFIG_PATH,  AUTOWARE_DEFAULT_MODULE_CONFIG_PATH)
from src.tools.autoware_tools.scenario_preprocessing import scenario_yaml_preprocessing
from src.tools.file_handling import delete_dir, move_dir, move_file


def move_scripts():
    if not os.path.exists(f"{MY_SCRIPTS_DIR}"):
        os.mkdir(f"{MY_SCRIPTS_DIR}")
    file_list = os.listdir(f"{PRE_SCRIPTS_DIR}")
    for file_name in file_list:
        if file_name not in ["dev.env", "requirements.sh"]:
            move_file(f"{PRE_SCRIPTS_DIR}/{file_name}", f"{MY_SCRIPTS_DIR}/{file_name}")


def scripts_preprocessing(file_name):
    with open(f"{PRE_SCRIPTS_DIR}/{file_name}", "r") as f:
        lines = f.read()
    with open(f"{PRE_SCRIPTS_DIR}/{file_name}", "w") as f:
        f.write(lines.replace("/home/cloudsky", DIR_ROOT))


def move_launch_file():
    os.system(
        f"cp -rf {PROJECT_ROOT}/data/config_files/planning_simulator.launch.xml {ADS_ROOT}/src/launcher/autoware_launch/autoware_launch/launch/planning_simulator.launch.xml")


def init_prepare():
    scripts_preprocessing("run_scenario.sh")
    scripts_preprocessing(".bashrc")
    scripts_preprocessing("move_bashrc.sh")
    scripts_preprocessing("extract_env.sh")
    scripts_preprocessing("kill_process.sh")
    scripts_preprocessing("setup_env.sh")
    scripts_preprocessing("dev.env")

    move_scripts()
    move_launch_file()
    delete_dir(AUTOWARE_CURRENT_MODULE_CONFIG_PATH, False)
    move_dir(AUTOWARE_DEFAULT_MODULE_CONFIG_PATH, AUTOWARE_CURRENT_MODULE_CONFIG_PATH)


if __name__ == '__main__':
    scenario_yaml_preprocessing()
    init_prepare()
