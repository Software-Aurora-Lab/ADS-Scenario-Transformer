from scenario_transfer.transformer.scenario_transformer import ScenarioTransformer, ScenarioTransformerConfiguration
from scenario_transfer.openscenario import OpenScenarioEncoder

def test_scenario_transformer(borregas_apollo_scenario9_path,
                              borregas_vector_map_path,
                              borregas_apollo_map_path):

    configuration = ScenarioTransformerConfiguration(
        apollo_scenario_path=borregas_apollo_scenario9_path,
        apollo_hd_map_path=borregas_apollo_map_path,
        vector_map_path=borregas_vector_map_path)
    transformer = ScenarioTransformer(configuration=configuration)

    scenario = transformer.transform()
    
    assert len(transformer.entities) == 7
