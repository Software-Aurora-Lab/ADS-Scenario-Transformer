from copy import deepcopy
import pandas as pd
from src.config import MODULE_ORACLES, DETERMINISM_CONFIRMED_TIMES
from duplicate_elimination.Eliminator import Eliminator
from scenario_handling.ScenarioReplayer import replay_scenarios_in_threading


def compare_similarity(features, default_features_list):
    pd_default_features = pd.DataFrame(default_features_list)
    df_new_row = pd.DataFrame([features])
    pd_all_features = pd.concat([pd_default_features, df_new_row])
    eliminator = Eliminator()
    pd_features = pd_all_features.iloc[:, :]
    db_clusters, all_vio, unique_vio, elim_ratio = eliminator.cluster(pd_features)
    pd_all_features.insert(0, "clusters", db_clusters, True)
    cluster_id = db_clusters[-1]
    if cluster_id not in db_clusters[:-1]:
        check_similar = False
    else:
        check_similar = True
    return check_similar


def check_emerged_violations(violation_results, default_violations_results):
    violations_emerged_results = []
    for violation in violation_results:
        if violation.main_type in MODULE_ORACLES:
            violations_emerged_results.append(violation)
        else:
            default_features_list = [d.features for d in default_violations_results if
                                     d.main_type == violation.main_type]
            if not default_features_list:
                violations_emerged_results.append(violation)
            else:
                check_similar = compare_similarity(violation.features, default_features_list)
                if not check_similar:
                    violations_emerged_results.append(violation)
    return violations_emerged_results


def confirm_determinism(scenario, containers, first_violations_emerged_results, rerun_times):
    rerun_scenario_list = []
    for i in range(rerun_times):
        temp_scenario = deepcopy(scenario)
        temp_record_name = f"{temp_scenario.record_name}_rerun_{i}"
        temp_scenario.update_record_name(temp_record_name)
        temp_scenario.copy_temp_scenario_file()
        rerun_scenario_list.append(temp_scenario)

    print(f"------------Rerunning {scenario.record_name}-------------")
    replay_scenarios_in_threading(rerun_scenario_list, containers)
    accumulated_emerged_results_count_dict = {}
    all_emerged_results = []
    accumulated_emerged_results = []
    for temp_scenario in rerun_scenario_list:
        temp_scenario.update_scenario_record_dir_info()

        violation_results = temp_scenario.measure_violations()
        violations_emerged_results = check_emerged_violations(violation_results,
                                                              temp_scenario.original_violation_results)
        accumulated_emerged_results += violations_emerged_results
        for violation in violation_results:
            if violation not in all_emerged_results:
                all_emerged_results.append(violation)
        temp_scenario.delete_record()
        temp_scenario.delete_scenario_file()
    for emerged_violation in first_violations_emerged_results + accumulated_emerged_results:
        if emerged_violation.main_type not in accumulated_emerged_results_count_dict.keys():
            accumulated_emerged_results_count_dict[emerged_violation.main_type] = [emerged_violation]
        else:
            accumulated_emerged_results_count_dict[emerged_violation.main_type].append(emerged_violation)
    determined_emerged_results = [v[0] for v in accumulated_emerged_results_count_dict.values() if
                                  len(v) >= DETERMINISM_CONFIRMED_TIMES]
    print("-------------------------------------------------")
    return determined_emerged_results, all_emerged_results


