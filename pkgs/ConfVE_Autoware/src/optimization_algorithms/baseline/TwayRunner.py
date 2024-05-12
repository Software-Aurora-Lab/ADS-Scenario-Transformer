import time
from src.config import T_STRENGTH_VALUE, TIME_HOUR_THRESHOLD, POP_SIZE
from optimization_algorithms.TestRunner import TestRunner
from optimization_algorithms.baseline.TwiseTuner import TwiseTuner
from optimization_algorithms.genetic_algorithm.ga import generate_individuals


class TwayRunner(TestRunner):
    def __init__(self, containers):
        super().__init__(containers)
        self.twise_tuner = TwiseTuner(self.config_file_obj, self.range_analyzer, T=T_STRENGTH_VALUE)
        self.tway_runner()

    def tway_runner(self):
        # print("Start T-way")

        while True:
            for inner_loop_i in range(POP_SIZE):
                default_individual = generate_individuals(self.config_file_obj, population_size=1)[0]
                generated_individual = self.twise_tuner.tune_individual(default_individual, self.range_analyzer)
                ind_id = f"Config_{self.individual_num}"

                self.individual_running(generated_individual, ind_id)

                if time.time() - self.runner_time >= TIME_HOUR_THRESHOLD * 3600:
                    return

            # output range analysis every generation
            self.file_output_manager.update_range_analysis_file(self.config_file_obj, self.range_analyzer,
                                                                self.individual_num)
            self.record_replace_and_check()
