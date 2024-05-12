import ruamel.yaml


class AutowareTranslator:

    @staticmethod
    def option_obj_translator(option_obj_list, tuned_id_list):
        ruamel_yaml = ruamel.yaml.YAML(typ=['rt', 'string'])
        ruamel_yaml.preserve_quotes = True
        group_id_dict = {}

        for tuned_id in tuned_id_list:
            option_obj = option_obj_list[tuned_id]
            if option_obj.config_file_path not in group_id_dict:
                group_id_dict[option_obj.config_file_path] = [tuned_id]
            else:
                group_id_dict[option_obj.config_file_path].append(tuned_id)

        for config_file_path, tuned_id_list in group_id_dict.items():
            ruamel_yaml_config_file = option_obj_list[tuned_id_list[0]].ruamel_yaml_config_file
            for tuned_id in tuned_id_list:
                option_obj = option_obj_list[tuned_id]
                temp_value = ruamel_yaml_config_file
                for layer in option_obj.layers:
                    temp_value = temp_value[layer]
                processed_option_value = option_obj.option_value
                temp_value[option_obj.option_key] = processed_option_value

            with open(config_file_path, 'w') as write_file:
                data_str = ruamel_yaml.dump_to_string(ruamel_yaml_config_file)
                write_file.write(data_str)
