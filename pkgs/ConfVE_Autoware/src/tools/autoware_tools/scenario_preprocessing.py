import glob
import ruamel.yaml
from src.config import ADS_SCENARIO_DIR, ADS_MAP_DIR

def scenario_yaml_preprocessing():
    scenario_file_path_list = glob.glob(ADS_SCENARIO_DIR + '/**/*.yaml', recursive=True)
    print(f"Processing {len(scenario_file_path_list)} scenario files...")

    file_count = 0
    for scenario_file_path in scenario_file_path_list:
        ruamel_yaml = ruamel.yaml.YAML()
        with open(scenario_file_path, "r") as read_file:
            ruamel_yaml_scenario_file = ruamel_yaml.load(read_file)
        logic_file_path = ruamel_yaml_scenario_file['OpenSCENARIO']['RoadNetwork']['LogicFile']['filepath']
        scene_graph_file_path = ruamel_yaml_scenario_file['OpenSCENARIO']['RoadNetwork']['SceneGraphFile']['filepath']
        ruamel_yaml_scenario_file['OpenSCENARIO']['RoadNetwork']['LogicFile']['filepath'] = ADS_MAP_DIR +"/" + logic_file_path.split('/maps/')[-1]
        ruamel_yaml_scenario_file['OpenSCENARIO']['RoadNetwork']['SceneGraphFile']['filepath'] = ADS_MAP_DIR + "/" + scene_graph_file_path.split('/maps/')[-1]


        values_list = ruamel_yaml_scenario_file['ScenarioModifiers']['ScenarioModifier']
        for value_list in values_list:
            if "list" in value_list.keys():
                value_list['list'] = [value_list['list'][0]]

        with open(scenario_file_path, 'w') as write_file:
            ruamel_yaml.dump(ruamel_yaml_scenario_file, write_file)
        file_count += 1

    print(f"Processed {file_count} scenario files")

if __name__ == '__main__':
    scenario_yaml_preprocessing()