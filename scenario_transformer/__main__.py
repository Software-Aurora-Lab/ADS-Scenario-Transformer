import argparse
from pathlib import Path
from scenario_transformer.transformer.scenario_transformer import ScenarioTransformerConfiguration, ScenarioTransformer
from scenario_transformer.openscenario.openscenario_coder import OpenScenarioEncoder


def main():
    parser = argparse.ArgumentParser(description="ADS Scenario Transformer")

    parser.add_argument("--apollo-scenario-path",
                        required=True,
                        help="Path to Apollo scenario files.")
    parser.add_argument("--apollo-map-path",
                        required=True,
                        help="Path to Apollo HD map data.")
    parser.add_argument("--vector-map-path",
                        required=True,
                        help="Path to vector map data.")
    parser.add_argument(
        "--road-network-pcd-map-path",
        required=False,
        default="point_cloud.pcd",
        help="RoadNetwork point cloud map path marked in scenario file.")
    parser.add_argument(
        "--road-network-lanelet-map-path",
        required=False,
        help="RoadNetwork Lanelet map path marked in scenario file.")
    parser.add_argument("--output-scenario-path",
                        required=False,
                        default="./",
                        help="Output scenario path.")
    parser.add_argument("--source-name",
                        required=False,
                        help="Input scenario source")

    parser.add_argument(
        "--obstacle-threshold",
        type=float,
        default=60.0,
        help="Threshold for obstacle direction change detection (in degrees).")
    parser.add_argument("--enable-traffic-signal",
                        action="store_false",
                        help="Enable processing of traffic signals.")
    parser.add_argument("--use-last-position-destination",
                        action="store_false",
                        help="Use the last known position as the destination.")

    args = parser.parse_args()

    configuration = ScenarioTransformerConfiguration(
        apollo_scenario_path=args.apollo_scenario_path,
        apollo_hd_map_path=args.apollo_map_path,
        vector_map_path=args.vector_map_path,
        road_network_pcd_map_path=args.road_network_pcd_map_path,
        road_network_lanelet_map_path=args.road_network_lanelet_map_path,
        obstacle_direction_change_detection_threshold=args.obstacle_threshold,
        enable_traffic_signal=args.enable_traffic_signal,
        use_last_position_as_destination=args.use_last_position_destination)

    transformer = ScenarioTransformer(configuration=configuration)
    scenario = transformer.transform()
    scenario_yaml = OpenScenarioEncoder.encode_proto_pyobject_to_yaml(
        proto_pyobject=scenario, wrap_result_with_typename=False)

    filename = ""
    if args.source_name:
        filename = args.source_name
        filename = filename + "-" + Path(args.apollo_scenario_path).stem
    else:
        filename = Path(args.apollo_scenario_path).stem

    output_path = Path(args.output_scenario_path) / (filename + ".yaml")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as file:
        file.write(scenario_yaml)

    print(f"File written to {output_path}")


if __name__ == "__main__":
    main()

# poetry run python -m scenario_transformer.__main__ \
# --apollo-map-path "./samples/map/BorregasAve/base_map.bin" \
# --vector-map-path "./samples/map/BorregasAve/lanelet2_map.osm" \
# --apollo-scenario-path "/home/sora/Desktop/changnam/ADS_DataSet/DoppelTest_borregas_ave_30/00000009.00000" \
# --road-network-lanelet-map-path "/home/sora/Desktop/changnam/autoware_map/borregasave_map/lanelet2_map.osm" \
# --source-name "DoppelTest"
