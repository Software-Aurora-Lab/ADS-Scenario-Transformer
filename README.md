# ADS Scenario Transformer

ADS Scenario Transformer transfers scenarios running on Apollo and SimControl environments to scenarios running on Autoware and TIER IV Scenario Simulator v2 environments. The transformation process targets two critical elements of a driving scenario: (1) the movement patterns of obstacles within the simulation, and (2) the status changes of traffic signals.

<img width="1363" alt="comparison1" src="https://github.com/hcn1519/ADS-Scenario-Transformer/assets/13018877/26673673-23a0-48f0-bb70-73de3f65050b">

## Prerequisites

- Python 3.10
- Linux OS

## Installation

Clone this project and execute setup_env script.

```shell
git clone https://github.com/hcn1519/ADS-Scenario-Transformer.git
source ./scripts/setup_env.sh
```

## Usage

### 1. Running Transformation

We have a script to run the transformer for transforming multiple scenarios at once.

```shell
poetry run python3 scripts/run_transformer.py <apollo_scenario_dir_path> <config_file_path>
```

This command transforms all scenarios in `<apollo_scenario_dir_path>` using the configuration defined in `<config_file_path>`. For example:

```shell
poetry run python3 scripts/run_transformer.py ../ADS_DataSet/DoppelTest_borregas_ave_30 ./scripts/config/borregasave_doppeltest.json
```

Running the transformer requires many arguments, which are listed [here](https://github.com/hcn1519/ADS-Scenario-Transformer/blob/main/ads_scenario_transformer/__main__.py). You can define them in a configuration file in JSON format like below:

```json
{
    "apollo-map-path": "./samples/map/BorregasAve/base_map.pickle",
    "vector-map-path": "./samples/map/BorregasAve/lanelet2_map.osm",
    "road-network-lanelet-map-path": "/home/sora/Desktop/changnam/autoware_map/BorregasAve/lanelet2_map.osm",
    "source-name": "BorregasAve-DoppelTest",
    "obstacle-waypoint-frequency": 5,
    "output-scenario-path": "./BorregasAve",
    "disable-traffic-signal": false,
    "use-last-position-destination": true,
    "add-violation-detecting-conditions": true
}
```

### 2. Running Scenarios in Docker

We also support a script for running scenarios in Docker. We play the scenario through this [prebuilt image](https://hub.docker.com/r/hcn1519/humble-202402-prebuilt-cuda-with-simulator) of Scenario Simulator and Autoware.

To play scenarios, first locate the scenario directories in `./experiments/exp_<unique_experiment_id>/scenarios/`.

The experiment running script can be run with the following command:

```shell
poetry run python3 scripts/scenario_player/experiment_runner.py --experiment_id <unique_experiment_id> \
--docker_image_id <docker_image_id> \
--map_path <map_directory_path> \
--enable_third_person_view \
--display_gui
```

For example:

```shell
poetry run python3 scripts/scenario_player/experiment_runner.py --experiment_id 5 \ 
--docker_image_id 6f0050135292 \
--map_path ./samples/map \
--enable_third_person_view \
--display_gui
```
