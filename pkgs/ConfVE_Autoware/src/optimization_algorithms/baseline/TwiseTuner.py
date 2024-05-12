import random
import itertools as it


class TwiseTuner:
    pair_list: list

    def __init__(self, config_file_obj, range_analyzer, T):
        self.T = T
        self.pair_index = 0
        self.config_file_obj = config_file_obj
        self.range_analyzer = range_analyzer
        self.pair_list = self.generate_pair_list()

    def decide_positions(self):
        position_tuple = self.pair_list[self.pair_index]
        self.pair_index += 1
        return position_tuple

    def tune_individual(self, individual, range_analyzer):
        position_tuple = self.decide_positions()
        for tuned_id in position_tuple:
            range_analyzer.tune_one_value(individual, self.config_file_obj, tuned_id)
        return individual

    def generate_pair_list(self):
        pair_list = []
        for e in it.combinations(range(self.config_file_obj.option_count), self.T):
            pair_list.append(e)
        random.shuffle(pair_list)
        return pair_list
