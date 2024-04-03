from openscenario_msgs import Scenario
from scenario_transfer.builder.scenario_builder import ScenarioBuilder, ScenarioConfiguration
from scenario_transfer.builder.entities_builder import EntityType


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
