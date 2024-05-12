import os
import time
import warnings
warnings.filterwarnings('ignore')
import pandas
from src.config import ADS_ROOT, DOCKER_CONTAINER_NAME, PROJECT_ROOT, AUTOWARE_CMD_PREPARE_TIME
from environment.Container import Container
from prepare import init_prepare
from scenario_handling.MessageGenerator import MessageGenerator
from scenario_handling.Scenario import Scenario
from scenario_handling.ScenarioReplayer import replay_scenario
from src.tools.autoware_tools.fitness_calculation import analyze_decision, analyze_sinuosity


init_prepare()

ctn = Container(ADS_ROOT, DOCKER_CONTAINER_NAME)
ctn.env_init()

message_generator = MessageGenerator()

scenario_recordname_list = message_generator.scenario_recordname_list
scenario_recordpath_list = message_generator.scenario_record_path_list

scenario_list = []
existed_scenario_recordname_list = []
# check if the ranking file exists, if not, create it
if not os.path.exists(f"{PROJECT_ROOT}/data/ranking.csv"):
    with open(f"{PROJECT_ROOT}/data/ranking.csv", "w") as ranking_file:
        ranking_file.write(
            f"scenario_record_name,map_name,duration,analysis_time,scenario_violation_count,scenario_decision_count,scenario_sinuosity,violations\n")
    scenario_count = 0
else:
    # read the csvfile and get the scenario_recordname_list
    csv_fle = pandas.read_csv(f"{PROJECT_ROOT}/data/ranking.csv")
    existed_scenario_recordname_list = list(csv_fle["scenario_record_name"])
    scenario_count = len(existed_scenario_recordname_list)

for scenario_recordpath, scenario_recordname in zip(scenario_recordpath_list, scenario_recordname_list):
    scenario = Scenario(scenario_recordname)
    scenario.initial_scenario_record_path = scenario_recordpath
    scenario.extract_map_name()
    scenario_list.append(scenario)

# scenario_ranking_list = []
for scenario in scenario_list:
    if scenario.record_name in existed_scenario_recordname_list:
        continue
    scenario_count += 1
    print(f"Scenario {scenario_count} / {len(scenario_list)}:")

    t0 = time.time()
    replay_scenario(scenario, ctn)

    t1 = time.time()
    scenario.violation_results = scenario.measure_violations()
    scenario.decision = analyze_decision(scenario.record_dir)
    scenario.sinuosity = analyze_sinuosity(scenario.record_dir)
    t2 = time.time()

    scenario.duration = t1 - t0 - AUTOWARE_CMD_PREPARE_TIME
    scenario.analysis_time = t2 - t1

    vio_str = ""
    for vio in scenario.violation_results:
        vio_str += f"{vio.main_type} "

    print(f"    {scenario.record_name}, duration: {scenario.duration:.2f}s, analysis time: {scenario.analysis_time:.2f}s, violation num: {len(scenario.violation_results)}, decision: {scenario.decision}, sinuosity: {scenario.sinuosity}, {vio_str}")

    with open(f"{PROJECT_ROOT}/data/ranking.csv", "a") as ranking_file:
        ranking_file.write(
            f"{scenario.record_name},{scenario.map_name},{scenario.duration},{scenario.analysis_time},{len(scenario.violation_results)},{scenario.decision},{scenario.sinuosity},{vio_str}\n")

    # scenario_ranking_list.append((len(scenario.violation_results), scenario.decision, scenario.sinuosity))
    scenario.delete_record()

# fronts_index_list = sort_nondominated(scenario_ranking_list)
# distances_list = crowding_dist(scenario_ranking_list)







# select_counter = 0
# selected_index_list = []
# for sub_fronts_list in fronts_index_list:
#     if select_counter + len(sub_fronts_list) < POP_SIZE:
#         selected_index_list += sub_fronts_list
#         select_counter += len(sub_fronts_list)
#     else:
#         sub_indexed_distances = [(index, distances_list[index]) for index in sub_fronts_list]
#         sub_indexed_distances.sort(reverse=True, key=lambda x: x[1])
#         sub_select_num = POP_SIZE - select_counter
#         for index, distance in sub_indexed_distances[:sub_select_num]:
#             selected_index_list.append(index)
#         break

# ranked_scenario_list = [scenario_list[index] for index in fronts_index_list]
# with open(f"{PROJECT_ROOT}/data/ranked.txt", "w") as ranking_file:
#     for scenario in ranked_scenario_list:
#         vio_str = ""
#         for vio in scenario.violation_results:
#             vio_str += f"{vio.main_type} "
#         ranking_file.write(
#             f"{scenario.record_name},{scenario.map_name},{scenario.duration},{scenario.analysis_time},{len(scenario.violation_results)},{scenario.decision},{scenario.sinuosity},{vio_str}\n")
