import os
import time
from src.config import MAX_INITIAL_SCENARIOS, OPT_MODE, DO_RANGE_ANALYSIS, AUTOWARE_DEFAULT_CONFIG_DIR_PATH, \
    DEFAULT_CONFIG_FILE
from src.configurator.OptionTuningItem import OptionTuningItem
from src.configurator.autoware.AutowareParser import AutowareParser
from range_analysis.RangeAnalyzer import RangeAnalyzer
from scenario_handling.FileOutputManager import FileOutputManager
from scenario_handling.MessageGenerator import MessageGenerator
from scenario_handling.create_scenarios import create_scenarios
from scenario_handling.run_scenarios import check_default_running, run_scenarios_without_determinism_checking


class TestRunner:
    def __init__(self, containers):
        self.individual_num = 0
        self.scenario_rid_emergence_list = []
        self.message_generator = MessageGenerator()
        self.config_file_obj = AutowareParser.config_file_parser2obj(AUTOWARE_DEFAULT_CONFIG_DIR_PATH)
        self.file_output_manager = FileOutputManager()
        self.containers = containers
        self.range_analyzer = RangeAnalyzer(self.config_file_obj)

        if os.path.exists(self.file_output_manager.default_violation_dump_data_path):
            default_violation_results_list_with_sid = self.file_output_manager.load_default_violation_results_by_pickle()
            record_id_list = [i[0] for i in default_violation_results_list_with_sid]
            self.message_generator.get_record_info_by_record_id(record_id_list)
            self.message_generator.update_selected_records_violatioin_directly(default_violation_results_list_with_sid)
        else:
            self.message_generator.get_record_info_by_record_id(record_id_list=range(MAX_INITIAL_SCENARIOS))
            default_violation_results_list_with_sid = check_default_running(self.message_generator,
                                                                            self.config_file_obj,
                                                                            self.file_output_manager,
                                                                            self.containers)
            print("\nDefault Config Rerun - Initial Scenario Violation Info:")
            self.file_output_manager.dump_default_violation_results_by_pickle(default_violation_results_list_with_sid)
        self.runner_time = time.time()

    def individual_running(self, generated_individual, ind_id):
        # self.file_output_manager.delete_temp_files()
        print("-------------------------------------------------")
        print(ind_id)
        self.file_output_manager.report_tuning_situation(generated_individual, self.config_file_obj)

        generated_individual.update_id(ind_id)

        scenario_list = create_scenarios(generated_individual,
                                         self.config_file_obj,
                                         self.message_generator.pre_record_info_list,
                                         name_prefix=ind_id,
                                         default=DEFAULT_CONFIG_FILE)

        run_scenarios_without_determinism_checking(generated_individual, scenario_list, self.containers)
        generated_individual.generate_fitness()
        self.check_scenario_list_vio_emergence(scenario_list)
        self.file_output_manager.print_fitness_results(generated_individual)
        self.file_output_manager.save_total_violation_results(generated_individual, scenario_list)

        if len(generated_individual.violations_emerged_results) > 0:
            if generated_individual.option_tuning_tracking_list:
                option_tuning_item = generated_individual.option_tuning_tracking_list[-1]
            else:
                option_tuning_item = "default"

            if DO_RANGE_ANALYSIS and OPT_MODE == "GA" and \
                    not generated_individual.allow_selection and \
                    isinstance(option_tuning_item, OptionTuningItem) and \
                    option_tuning_item.option_type in ["float", "integer", "e_number"]:
                range_change_str = self.range_analyzer.range_analyze(option_tuning_item, self.config_file_obj)
            else:
                range_change_str = "  Range Change: default\n"

            self.file_output_manager.save_option_tuning_file(generated_individual,
                                                             ind_id,
                                                             option_tuning_item,
                                                             range_change_str)
            # self.file_output_manager.save_config_file(ind_id)
            self.file_output_manager.save_vio_features(generated_individual, scenario_list)
            self.file_output_manager.save_count_dict_file()
        self.individual_num += 1
        print(f"--------Running for {(time.time() - self.runner_time) / 3600} hours-----------")

    def record_replace_and_check(self):
        self.message_generator.replace_records(self.scenario_rid_emergence_list)
        _ = check_default_running(self.message_generator,
                                  self.config_file_obj,
                                  self.file_output_manager,
                                  self.containers)
        self.scenario_rid_emergence_list = []
        self.message_generator.update_total_violation_results()

    def check_scenario_list_vio_emergence(self, scenario_list):
        for scenario in scenario_list:
            if scenario.has_emerged_violations and not scenario.has_emerged_module_violations:
                if scenario.record_id not in self.scenario_rid_emergence_list:
                    self.scenario_rid_emergence_list.append(scenario.record_id)