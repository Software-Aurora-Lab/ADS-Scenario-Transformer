from scenario_transformer.tools.traffic_signal_mapper import TrafficSignalMapper


def test_traffic_signal_mapper(apollo_map_parser, vector_map_parser,
                               borregas_doppel_scenario9_path):
    traffic_signal_mapper = TrafficSignalMapper(
        apollo_map_parser=apollo_map_parser,
        vector_map_parser=vector_map_parser)

    id_map = traffic_signal_mapper.traffic_light_id_map

    assert id_map[
        "signal_0"].id == 494, "Expected signal_0 traffic_light ID to be 494"
    assert id_map[
        "signal_9"].id == 494, "Expected signal_9 traffic_light ID to be 494"
    assert id_map[
        "signal_13"].id == 494, "Expected signal_13 traffic_light ID to be 494"
    assert id_map[
        "signal_14"].id == 494, "Expected signal_14 traffic_light ID to be 494"

    assert id_map[
        "signal_1"].id == 520, "Expected signal_1 traffic_light ID to be 520"
    assert id_map[
        "signal_10"].id == 520, "Expected signal_10 traffic_light ID to be 520"
    assert id_map[
        "signal_11"].id == 520, "Expected signal_11 traffic_light ID to be 520"

    assert id_map[
        "signal_2"].id == 586, "Expected signal_2 traffic_light ID to be 586"
    assert id_map[
        "signal_5"].id == 586, "Expected signal_5 traffic_light ID to be 586"
    assert id_map[
        "signal_6"].id == 586, "Expected signal_6 traffic_light ID to be 586"
    assert id_map[
        "signal_12"].id == 586, "Expected signal_12 traffic_light ID to be 586"

    assert id_map[
        "signal_3"].id == 553, "Expected signal_3 traffic_light ID to be 553"
    assert id_map[
        "signal_4"].id == 553, "Expected signal_4 traffic_light ID to be 553"
    assert id_map[
        "signal_7"].id == 553, "Expected signal_7 traffic_light ID to be 553"
    assert id_map[
        "signal_8"].id == 553, "Expected signal_8 traffic_light ID to be 553"
