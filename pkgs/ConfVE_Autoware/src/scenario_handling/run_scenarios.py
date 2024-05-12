import time
from scenario_handling.ScenarioReplayer import replay_scenarios_in_threading
from scenario_handling.create_scenarios import create_scenarios, create_scenario
from optimization_algorithms.genetic_algorithm.ga import generate_individuals
from duplicate_elimination.ViolationChecker import check_emerged_violations, confirm_determinism
from src.config import DEFAULT_DETERMINISM_RERUN_TIMES, MODULE_ORACLES


def run_default_scenarios(scenario_list, containers, message_generator):
    default_violation_results_list = []
    for scenario in scenario_list:
        all_emerged_results = []
        contain_module_violation = True
        while contain_module_violation:
            _, all_emerged_results = confirm_determinism(scenario,
                                                         containers,
                                                         first_violations_emerged_results=[],
                                                         rerun_times=DEFAULT_DETERMINISM_RERUN_TIMES)
            contain_module_violation = check_module_failure(all_emerged_results, MODULE_ORACLES)
            if contain_module_violation:
                pre_record_info = message_generator.replace_record(scenario.record_id)
                scenario = create_scenario(pre_record_info, name_prefix="default", config_file_tuned_status=True)
        default_violation_results_list.append((scenario.record_id, all_emerged_results))
    return default_violation_results_list


def run_scenarios_without_determinism_checking(generated_individual, scenario_list, containers):
    # print("Normal Run...")
    start_time = time.time()
    replay_scenarios_in_threading(scenario_list, containers)

    for scenario in scenario_list:
        violation_results = scenario.measure_violations()
        violations_emerged_results = check_emerged_violations(violation_results, scenario.original_violation_results)
        contain_module_violation = check_module_failure(violations_emerged_results, oracles=MODULE_ORACLES)
        if generated_individual.allow_selection:
            generated_individual.update_allow_selection(contain_module_violation)
        scenario.update_emerged_status(violations_emerged_results, contain_module_violation)
        generated_individual.update_fitness(violations_emerged_results, violation_results, scenario)
        scenario.delete_record()
    total_time = time.time() - start_time
    generated_individual.update_exec_time(total_time)


def check_module_failure(violations_emerged_results, oracles):
    for emerged_violation in violations_emerged_results:
        if emerged_violation.main_type in oracles:
            print(f"    Contain module violation: {emerged_violation.main_type}")
            return True
    return False


def check_emerged_violations_for_tuple(violation_results, scenario):
    violations_emerged_results = []
    violations_removed_results = []
    for violation in violation_results:
        if violation not in scenario.original_violation_results:
            violations_emerged_results.append(violation)
    for violation in scenario.original_violation_results:
        if violation not in violation_results:
            violations_removed_results.append(violation)
    return violations_emerged_results, violations_removed_results


def check_default_running(message_generator, config_file_obj, file_output_manager, containers):
    selected_pre_record_info_list = message_generator.get_not_rerun_record()
    default_violation_results_list = []
    if selected_pre_record_info_list:
        name_prefix = "default"
        file_output_manager.output_initial_record2default_mapping(message_generator.pre_record_info_list, name_prefix)
        default_individual = generate_individuals(config_file_obj, population_size=1)[0]
        scenario_list = create_scenarios(default_individual,
                                         config_file_obj,
                                         selected_pre_record_info_list,
                                         name_prefix,
                                         default=True)
        default_violation_results_list = run_default_scenarios(scenario_list, containers, message_generator)
        message_generator.update_selected_records_violatioin_directly(default_violation_results_list)
    return default_violation_results_list
