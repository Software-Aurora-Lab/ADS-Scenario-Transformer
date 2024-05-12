from copy import deepcopy
from src.tools.autoware_tools.fitness_calculation import analyze_decision, analyze_sinuosity


class IndividualWithFitness:

    def __init__(self, value_list):
        self.value_list = value_list
        self.pre_value_list = []
        self.option_tuning_tracking_list = []
        self.reset_default()

    def configuration_reverting(self, do_reverting):
        if do_reverting:
            temp = deepcopy(self.value_list)
            self.value_list = deepcopy(self.pre_value_list)
            self.pre_value_list = temp
            self.option_tuning_tracking_list.pop()
            self.reset_default()

    def update_exec_time(self, total_time):
        self.execution_time = total_time

    def update_allow_selection(self, contain_module_violation):
        self.allow_selection = not contain_module_violation

    def update_id(self, id):
        self.id = id

    def reset_default(self):
        self.fitness = None
        self.allow_selection = True
        self.violation_results_list = []
        self.violations_emerged_results = []
        self.decision_list = []
        self.sinuosity_list = []

    def update_fitness(self, violations_emerged_results, violation_results, scenario):
        violations_emerged_results_with_sid = [(scenario.record_id, v) for v in violations_emerged_results]
        self.violations_emerged_results += violations_emerged_results_with_sid
        self.violation_results_list.append(violation_results)
        decision = analyze_decision(scenario.record_dir)
        sinuosity = analyze_sinuosity(scenario.record_dir)
        self.decision_list.append(decision)
        self.sinuosity_list.append(sinuosity)

    def generate_fitness(self):
        emerged_violations_count = len(self.violations_emerged_results)

        count_type_list = []
        for emerged_vio in self.violations_emerged_results:
            main_type = emerged_vio[1].main_type
            if main_type not in count_type_list:
                count_type_list.append(main_type)

        emerged_violations_type_count = len(count_type_list)

        total_decision_count = sum(self.decision_list)
        avg_sinuosity = sum(self.sinuosity_list) / len(self.sinuosity_list)

        self.fitness = (emerged_violations_count, emerged_violations_type_count, total_decision_count, avg_sinuosity)
