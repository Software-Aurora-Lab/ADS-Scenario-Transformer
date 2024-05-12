from src.config import AUTOWARE_CURRENT_CONFIG_DIR_PATH, AUTOWARE_DEFAULT_CONFIG_DIR_PATH


class OptionObj:
    def __init__(self, option_id, option_key, option_value, option_type, position, layers):
        self.option_id = option_id
        self.option_key = option_key
        self.option_value = option_value
        self.option_type = option_type
        self.position = position
        self.layers = layers
        self.config_file_path = None

    def update_config_file_path(self, default_config_file_path):
        self.config_file_path = AUTOWARE_CURRENT_CONFIG_DIR_PATH + default_config_file_path.split(AUTOWARE_DEFAULT_CONFIG_DIR_PATH)[-1]

    def update_ruamel_yaml_config_file(self, ruamel_yaml_config_file):
        self.ruamel_yaml_config_file = ruamel_yaml_config_file
