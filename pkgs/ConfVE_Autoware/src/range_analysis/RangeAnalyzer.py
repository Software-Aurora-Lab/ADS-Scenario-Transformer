import math
from copy import deepcopy
from src.configurator.OptionTuningItem import OptionTuningItem
from src.configurator.MisInjTester import MisInjTester


class RangeAnalyzer:
    def __init__(self, config_file_obj):
        self.range_list = self.range_init(config_file_obj.option_type_list)
        self.original_range_list = deepcopy(self.range_list)

    def generate_option_range(self, option_type):
        # initial range should contain default option value
        if option_type == "float":
            option_range = [-10001, 10001]
        elif option_type == "integer":
            option_range = [-10001, 10001]
        elif option_type == "boolean":
            option_range = [True, False]
        elif option_type == "e_number":
            option_range = [-101, 101]  # e.g., [1e-100, 1e100]
        else:
            option_range = []
        return option_range

    def generate_new_range(self, cur_range, option_tuning_item, config_file_obj):
        cur_lower_bound = cur_range[0]
        cur_upper_bound = cur_range[1]

        default_option_value = config_file_obj.default_option_value_list[option_tuning_item.position]
        cur_option_value = option_tuning_item.cur_value

        if option_tuning_item.option_type == "e_number":
            default_exp_raw = default_option_value.split("e")[-1]
            if default_exp_raw[0:2] == "-0":
                default_exp = int(default_exp_raw[2:])
            elif default_exp_raw[0] == "0":
                default_exp = int(default_exp_raw[1:])
            else:
                default_exp = int(default_exp_raw)

            cur_exp = int(cur_option_value.split("e")[-1])

            if default_exp > cur_exp:
                new_range = [cur_exp+1, cur_upper_bound]
            elif default_exp < cur_exp:
                new_range = [cur_lower_bound, cur_exp-1]
            else:
                new_range = cur_range
        elif option_tuning_item.option_type == "boolean":
            new_range = cur_range
        else:
            default_value = eval(default_option_value)
            cur_value = eval(str(cur_option_value))
            if default_value > cur_value:
                new_range = [math.ceil(cur_value)+1, cur_upper_bound]
            elif default_value < cur_value:
                new_range = [cur_lower_bound, math.floor(cur_value)-1]
            else:
                new_range = cur_range
        return new_range

    def range_init(self, option_type_list):
        range_list = []
        for option_type in option_type_list:
            option_range = self.generate_option_range(option_type)
            range_list.append(option_range)
        return range_list

    def range_analyze(self, option_tuning_item, config_file_obj):
        cur_range = self.range_list[option_tuning_item.position]
        new_range = self.generate_new_range(cur_range, option_tuning_item, config_file_obj)
        self.range_list[option_tuning_item.position] = new_range
        range_change_str = f"  Range Change: {option_tuning_item.position}, {option_tuning_item.option_key}, {cur_range}->{new_range}\n"
        return range_change_str

    def tune_one_value(self, individual_obj, config_file_obj, tuned_id):
        option_type = config_file_obj.option_type_list[tuned_id]
        option_value = individual_obj.value_list[tuned_id]
        individual_obj.pre_value_list = deepcopy(individual_obj.value_list)

        mit_inj_tester = MisInjTester()
        generated_value = mit_inj_tester.apply_one_operator(option_type, option_value, self.range_list[tuned_id])

        individual_obj.value_list[tuned_id] = generated_value
        individual_obj.option_tuning_tracking_list.append(
            OptionTuningItem(tuned_id,
                             option_type,
                             config_file_obj.option_obj_list[tuned_id].option_key,
                             individual_obj.pre_value_list[tuned_id],
                             individual_obj.value_list[tuned_id],
                             config_file_obj.option_obj_list[tuned_id])
        )
