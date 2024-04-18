from scenario_transformer.transformer.scenario_transformer import ScenarioTransformer, ScenarioTransformerConfiguration
from scenario_transformer.openscenario import OpenScenarioEncoder


def test_scenario_transformer(borregas_apollo_scenario9_path,
                              borregas_vector_map_path,
                              borregas_apollo_map_path):

    configuration = ScenarioTransformerConfiguration(
        apollo_scenario_path=borregas_apollo_scenario9_path,
        apollo_hd_map_path=borregas_apollo_map_path,
        vector_map_path=borregas_vector_map_path,
        road_network_lanelet_map_path=
        "/home/sora/Desktop/changnam/autoware_map/borregasave_map/lanelet2_map.osm"
    )
    transformer = ScenarioTransformer(configuration=configuration)

    scenario = transformer.transform()

    encoded_scenario = OpenScenarioEncoder.encode_proto_pyobject_to_dict(
        proto_pyobject=scenario, wrap_result_with_typename=False)

    assert len(transformer.entities.scenarioObjects) == 7
    assert encoded_scenario['OpenSCENARIO']['RoadNetwork']['LogicFile'][
        'filepath'] == configuration.road_network_lanelet_map_path
    assert len(
        encoded_scenario['OpenSCENARIO']['Entities']['ScenarioObject']) == 7
    assert len(encoded_scenario['OpenSCENARIO']['Storyboard']['Story']) == 7
