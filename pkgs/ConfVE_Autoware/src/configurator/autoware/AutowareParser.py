import glob
import re
import ruamel.yaml
from copy import deepcopy
from src.configurator.OptionObj import OptionObj
from src.configurator.ConfigFileObj import ConfigFileObj
from src.config import AUTOWARE_DEFAULT_CONFIG_DIR_PATH
from src.configurator.autoware.AutowareTranslator import AutowareTranslator


class AutowareParser:
    key_stack = []
    option_obj_list = []
    option_count = 0

    @staticmethod
    def analyze_type(value):
        if re.fullmatch(r"-?\d+((\.\d+)|(\d*))e-?\d+(\d*)", str(value)):
            value_type = "e_number"
        elif isinstance(value, bool):
            value_type = "boolean"
        elif isinstance(value, float):
            value_type = "float"
        elif isinstance(value, int):
            value_type = "integer"
        elif isinstance(value, str):
            value_type = "string"
        elif isinstance(value, list):
            value_type = "list"
        else:
            value_type = None
        return value_type

    @staticmethod
    def get_str_value(value):
        if isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)

    @staticmethod
    def traverse_dict(dictionary, config_file_path, ruamel_yaml_config_file):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                AutowareParser.key_stack.append(key)
                AutowareParser.traverse_dict(value, config_file_path, ruamel_yaml_config_file)
                AutowareParser.key_stack.pop()
            else:
                option_obj = OptionObj(AutowareParser.option_count, key, AutowareParser.get_str_value(value),
                                       AutowareParser.analyze_type(value),
                                       [], deepcopy(AutowareParser.key_stack))
                option_obj.update_config_file_path(config_file_path)
                option_obj.update_ruamel_yaml_config_file(ruamel_yaml_config_file)
                AutowareParser.option_obj_list.append(option_obj)
                AutowareParser.option_count += 1

    @staticmethod
    def config_file_parser2obj(config_file_path):
        config_file_path_list = glob.glob(config_file_path + '/**/*.param.yaml', recursive=True)
        for config_file_path in config_file_path_list:
            ruamel_yaml = ruamel.yaml.YAML()
            ruamel_yaml.preserve_quotes = True
            with open(config_file_path, "r") as read_file:
                ruamel_yaml_config_file = ruamel_yaml.load(read_file)
            yaml_config_file_dict = eval(str(ruamel_yaml_config_file))
            AutowareParser.traverse_dict(yaml_config_file_dict, config_file_path, ruamel_yaml_config_file)
        config_file_obj = ConfigFileObj(AutowareParser.option_obj_list, AutowareParser.option_count)
        return config_file_obj


if __name__ == '__main__':
    config_file_obj = AutowareParser.config_file_parser2obj(AUTOWARE_DEFAULT_CONFIG_DIR_PATH)
    tuned_id_list = [3, 6, 250]
    new_option_list = config_file_obj.option_obj_list
    new_option_list[3].option_value = "0.5"
    new_option_list[6].option_value = "0.5"
    new_option_list[250].option_value = "0.5"
    output_file_tuple_list = AutowareTranslator.option_obj_translator(new_option_list, tuned_id_list)
