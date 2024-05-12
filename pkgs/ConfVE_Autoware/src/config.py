from pathlib import Path

"""
Global configurations for the framework
"""

#######################
## Customized Config ##
#######################

MAP_NAME = "LEO-VM"  # LEO-VM/awf_cicd/City/All
OPT_MODE = "GA"  # GA/T-way/ConfVD


####################
## Default Config ##
####################

# ENVIRONMENT SETTINGS
AV_TESTING_APPROACH = "AutowareScenarios"  # AutowareScenarios
DOCKER_CONTAINER_NAME = "confve_autoware"
MAX_RECORD_TIME = 60  # 10/30/50
AUTOWARE_CMD_PREPARE_TIME = 25
TIME_HOUR_THRESHOLD = 10  # hours
DEFAULT_SCRIPT_PORT = 5555
CONTAINER_NUM = 3  # 3/4/5
DOCKER_IMAGE_ID = "a70ab6378b29"

# TESTING SETTINGS
DEFAULT_CONFIG_FILE = False
IS_CUSTOMIZED_EPSILON = False
DO_RANGE_ANALYSIS = True
EPSILON_THRESHOLD = 1
T_STRENGTH_VALUE = 2  # 2: pairwise

# GA SETTINGS
GENERATION_LIMIT = 100
CX_P = 0.2
MUT_P = 0.8
SELECT_MODE = "nsga2"
SELECT_NUM_RATIO = [7, 2, 1]
POP_SIZE = 20  # 20

MAX_INITIAL_SCENARIOS = 9  # 8/9/10
DEFAULT_DETERMINISM_RERUN_TIMES = 6  # 4/5/6/10
DETERMINISM_CONFIRMED_TIMES = 4

MODULE_ORACLES = ["RoutingFailure",
                  "PredictionFailure",
                  "PlanningFailure",
                  "CarNeverMoved",
                  "SimControlFailure",
                  "PlanningGeneratesGarbage",
                  "ModuleDelayOracle",
                  "LocalizationFailure",
                  "SimulationFailure"]

INITIAL_EXP_NAME = f"{AV_TESTING_APPROACH}_{MAP_NAME}"
EXP_NAME_OPT_MODE = f"{INITIAL_EXP_NAME}_{OPT_MODE}"

# DIRECTORIES
DIR_ROOT = str(Path(__file__).parent.parent.parent)
PROJECT_ROOT = str(Path(__file__).parent.parent)
FEATURES_CSV_DIR = f'{PROJECT_ROOT}/data/violation_features'
EXP_GROUP_NAMING_TREE = f"{AV_TESTING_APPROACH}/{EXP_NAME_OPT_MODE}"
EXP_BASE_DIR = f"{PROJECT_ROOT}/data/exp_results/{EXP_GROUP_NAMING_TREE}"
BACKUP_SAVE_DIR = f'{DIR_ROOT}/Backup/{EXP_GROUP_NAMING_TREE}'
BACKUP_CONFIG_SAVE_DIR = f"{BACKUP_SAVE_DIR}/config_files"
BACKUP_RECORD_SAVE_DIR = f"{BACKUP_SAVE_DIR}/records"

ADS_ROOT = f'{DIR_ROOT}/autoware'
ADS_MAP_DIR = f'{DIR_ROOT}/autoware_map/autoware_scenario_data/maps'
ADS_SCENARIO_DIR = f'{DIR_ROOT}/autoware_map/autoware_scenario_data/scenarios'
ADS_TEMP_SCENARIO_DIR = f'{DIR_ROOT}/autoware_map/autoware_scenario_data/temp_scenarios'

TMP_RECORDS_DIR = f'/tmp/scenario_test_runner'
ADS_RECORDS_DIR = f'{ADS_ROOT}/records/records_for_analysis'

PRE_SCRIPTS_DIR = f'{PROJECT_ROOT}/data/scripts'
MY_SCRIPTS_DIR = f"{ADS_ROOT}/scripts"

TESTED_MODULE = "planning"
TESTED_PACKAGE = "planning/scenario_planning/lane_driving/behavior_planning/behavior_velocity_planner"
AUTOWARE_DEFAULT_CONFIG_DIR_PATH = f"{PROJECT_ROOT}/data/config_files/autoware/{TESTED_PACKAGE}"
AUTOWARE_CURRENT_CONFIG_DIR_PATH = f"{ADS_ROOT}/src/launcher/autoware_launch/autoware_launch/config/{TESTED_PACKAGE}"
AUTOWARE_DEFAULT_MODULE_CONFIG_PATH = f"{PROJECT_ROOT}/data/config_files/autoware/{TESTED_MODULE}"
AUTOWARE_CURRENT_MODULE_CONFIG_PATH = f"{ADS_ROOT}/src/launcher/autoware_launch/autoware_launch/config/{TESTED_MODULE}"

# VEHICLE CONFIGS FOR AUTOWARE
AUTOWARE_VEHICLE_LENGTH = 4.77
AUTOWARE_VEHICLE_WIDTH = 1.83
AUTOWARE_VEHICLE_HEIGHT = 2.5
AUTOWARE_VEHICLE_back_edge_to_center = 1.030

