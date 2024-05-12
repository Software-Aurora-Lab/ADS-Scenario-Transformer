import warnings
warnings.filterwarnings('ignore')
import pandas
from src.config import PROJECT_ROOT, ADS_SCENARIO_DIR
from optimization_algorithms.genetic_algorithm.nsga2 import sort_nondominated, crowding_dist
from scenario_handling.Scenario import Scenario

csv_fle = pandas.read_csv(f"{PROJECT_ROOT}/data/ranking.csv")
# existed_scenario_recordname_list = list(csv_fle["scenario_record_name"])
# scenario_count = len(existed_scenario_recordname_list)
scenario_ranking_list = []

# iterate over the rows of the csv file and create a list of tuples
scenario_list = []
for index, row in csv_fle.iterrows():
    scenario = Scenario(row["scenario_record_name"])
    # scenario.map_name = row["map_name"]
    scenario.initial_scenario_record_path = f"{ADS_SCENARIO_DIR}/{scenario.record_name}.yaml"
    scenario.extract_map_name()
    scenario.duration = row["duration"]
    scenario.analysis_time = row["analysis_time"]
    scenario.violation_count = row["scenario_violation_count"]
    scenario.decision = row["scenario_decision_count"]
    scenario.sinuosity = row["scenario_sinuosity"]
    scenario.violations = row["violations"]
    if scenario.sinuosity != 0 and "Failure" not in scenario.violations:
        scenario_list.append(scenario)
        scenario_ranking_list.append((scenario.violation_count, scenario.decision, scenario.sinuosity))


fronts_index_list = sort_nondominated(scenario_ranking_list)
distances_list = crowding_dist(scenario_ranking_list)

sorted_index_list = []
for sub_fronts_list in fronts_index_list:
    sub_indexed_distances = [(index, distances_list[index]) for index in sub_fronts_list]
    sub_indexed_distances.sort(reverse=True, key=lambda x: x[1])
    sorted_index_list += [index for index, distance in sub_indexed_distances]

ranked_scenario_list = [scenario_list[index] for index in sorted_index_list]
with open(f"{PROJECT_ROOT}/data/ranked.csv", "w") as ranking_file:
    ranking_file.write(
        f"scenario_record_name,map_name,duration,analysis_time,scenario_violation_count,scenario_decision_count,scenario_sinuosity,violations\n")
    for scenario in ranked_scenario_list:
        ranking_file.write(
            f"{scenario.record_name},{scenario.map_name},{scenario.duration},{scenario.analysis_time},{scenario.violation_count},{scenario.decision},{scenario.sinuosity},{scenario.violations}\n")
