import yaml
from definitions import TEST_ROOT
from openscenario_msgs import Scenario, Storyboard
from scenario_transformer.builder.scenario_builder import ScenarioBuilder, ScenarioConfiguration
from scenario_transformer.builder.entities_builder import EntityType
from scenario_transformer.openscenario import OpenScenarioEncoder, OpenScenarioDecoder


def test_scenario_builder(storyboard):
    scenario_config = ScenarioConfiguration(
        entities=[EntityType.EGO, EntityType.NPC, EntityType.NPC],
        lanelet_map_path="/home/map/lanelet2.osm",
        traffic_signals=[])
    scenario_builder = ScenarioBuilder(scenario_configuration=scenario_config)
    scenario_builder.make_scenario_definition(storyboard=storyboard)
    scenario = scenario_builder.get_result()

    assert isinstance(scenario, Scenario)
    assert scenario.openScenario.fileHeader.author == "ADS Scenario Tranformer"
    assert scenario.openScenario.roadNetwork.logicFile.filepath == "/home/map/lanelet2.osm"
    assert scenario.openScenario.storyboard == storyboard


def test_scenario_key_value(parameter_declarations):
    scenario_path = TEST_ROOT + "/data/scenario.yaml"
    storyboard_path = TEST_ROOT + "/data/scenario_storyboard.yaml"
    with open(scenario_path, 'r') as file:
        scenario_dict = yaml.safe_load(file)

    with open(storyboard_path, 'r') as file:
        storyboard_dict = yaml.safe_load(file)

    scenario_config = ScenarioConfiguration(
        entities=[EntityType.EGO, EntityType.NPC, EntityType.NPC],
        lanelet_map_path=
        "/home/cloudsky/autoware_map/autoware_scenario_data/maps/awf_cicd_virtual_G_dev/lanelet2_map.osm",
        pcd_map_path=
        "/home/cloudsky/autoware_map/autoware_scenario_data/maps/awf_cicd_virtual_G_dev/pointcloud_map.pcd",
        traffic_signals=[])

    storyboard_obj = OpenScenarioDecoder.decode_yaml_to_pyobject(
        yaml_dict=storyboard_dict,
        type_=Storyboard,
        exclude_top_level_key=True)

    scenario_builder = ScenarioBuilder(scenario_configuration=scenario_config)

    fileheader_dict = {
        "revMajor": 1,
        "revMinor": 1,
        "date": '2023-11-13T12:25:48.481Z',
        "author": 'AKIRA TAMURA (last modified by: Berkay Karaman)',
        "description": ""
    }
    scenario_builder.make_file_header(fileheader_dict=fileheader_dict)
    scenario_builder.make_scenario_definition(
        storyboard=storyboard_obj,
        parameter_declarataions=parameter_declarations.parameterDeclarations)
    scenario = scenario_builder.get_result()

    encoded_scenario = OpenScenarioEncoder.encode_proto_pyobject_to_dict(
        proto_pyobject=scenario, wrap_result_with_typename=False)

    assert_dicts_equal(encoded_scenario, scenario_dict)


def assert_dicts_equal(dict1, dict2):
    assert isinstance(dict1, dict), f"Lhs is not dict type: {type(dict1)}"
    assert isinstance(dict2, dict), f"Rhs is not dict type: {type(dict2)}"

    assert set(dict1.keys()) == set(
        dict2.keys()), "Keys of dictionaries are not the same"

    for key in dict1:
        if isinstance(dict1[key], dict):
            assert_dicts_equal(dict1[key], dict2[key])
        elif isinstance(dict1[key], list):
            for el1, el2 in zip(dict1[key], dict2[key]):
                assert_dicts_equal(el1, el2)
        else:
            assert dict1[key] == dict2[
                key], f"Values for key {key} are not the same v1: {dict1[key]}, v2: {dict2[key]}"
