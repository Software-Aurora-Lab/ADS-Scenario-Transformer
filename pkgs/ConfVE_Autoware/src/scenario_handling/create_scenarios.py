from copy import deepcopy
from src.config import AUTOWARE_CURRENT_CONFIG_DIR_PATH, AUTOWARE_DEFAULT_CONFIG_DIR_PATH
from src.configurator.autoware.AutowareTranslator import AutowareTranslator
from scenario_handling.Scenario import Scenario
from src.tools.file_handling import delete_dir, move_dir


def config_file_generating(generated_individual, config_file_obj, default):
    new_option_obj_list = deepcopy(config_file_obj.option_obj_list)
    delete_dir(AUTOWARE_CURRENT_CONFIG_DIR_PATH, False)
    move_dir(AUTOWARE_DEFAULT_CONFIG_DIR_PATH, AUTOWARE_CURRENT_CONFIG_DIR_PATH)
    config_file_tuned_status = False  # config file not tuned
    if not default:
        generated_value_list = generated_individual.value_list
        tuned_id_list = []
        for generated_value, option_obj in zip(generated_value_list, new_option_obj_list):
            if option_obj.option_value != generated_value:
                option_obj.option_value = generated_value
                tuned_id_list.append(option_obj.option_id)
        AutowareTranslator.option_obj_translator(new_option_obj_list, tuned_id_list)
        config_file_tuned_status = True  # config file tuned
    return config_file_tuned_status


def create_scenarios(generated_individual, config_file_obj, pre_record_info_list, name_prefix, default):
    config_file_tuned_status = config_file_generating(generated_individual, config_file_obj, default)
    scenario_list = []
    for pre_record_info in pre_record_info_list:
        scenario = create_scenario(pre_record_info, name_prefix, config_file_tuned_status)
        scenario_list.append(scenario)
    return scenario_list


def create_scenario(pre_record_info, name_prefix, config_file_tuned_status):
    record_name = pre_record_info.record_name
    scenario = Scenario(record_name)
    scenario.update_record_id(pre_record_info.record_id)
    scenario.update_config_file_status(config_file_tuned_status)
    scenario.update_record_info(pre_record_info)
    return scenario
