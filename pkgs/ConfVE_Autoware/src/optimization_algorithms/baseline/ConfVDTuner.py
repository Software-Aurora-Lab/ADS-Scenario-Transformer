import random


class ConfVDTuner:
    id_list: list

    def __init__(self, config_file_obj, range_analyzer):
        self.config_file_obj = config_file_obj


    def tune_individual(self, individual, range_analyzer):
        tuned_id = random.randint(0, self.config_file_obj.option_count - 1)
        range_analyzer.tune_one_value(individual, self.config_file_obj, tuned_id)
        return individual
