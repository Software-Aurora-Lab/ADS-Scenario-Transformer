import unittest
import yaml
from definitions import TEST_ROOT
from openscenario_msgs import Route, LanePosition, ObjectController, Vehicle, EntityObject, ScenarioObject, Entities, ParameterDeclarations
from scenario_transfer.openscenario import OpenScenarioEncoder, OpenScenarioDecoder


class TestOpenScenarioCoder(unittest.TestCase):

    def setUp(self):
        self.route_file_path = TEST_ROOT + "/data/openscenario_route.yaml"
        self.entities_file_path = TEST_ROOT + "/data/openscenario_entities.yaml"
        self.scenario_object_file_path = TEST_ROOT + "/data/openscenario_scenario_object.yaml"

    def test_openscenario_encode_decode(self):
        with open(self.route_file_path, 'r') as file:
            input = file.read()

        dict = yaml.safe_load(input)
        openscenario_route = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict, type_=Route, exclude_top_level_key=True)
        encoded_data = OpenScenarioEncoder.encode_proto_pyobject_to_yaml(
            openscenario_route)

        decoded_data = yaml.safe_load(encoded_data)

        self.assertIsNotNone(decoded_data["Route"])
        self.assertIsNotNone(decoded_data["Route"]["Waypoint"])
        self.assertIsInstance(decoded_data["Route"]["Waypoint"], list)
        self.assertIsNotNone(decoded_data["Route"]["Waypoint"][0]["Position"])
        self.assertIsNotNone(
            decoded_data["Route"]["Waypoint"][0]["Position"]["LanePosition"])

        openscenario_route = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=decoded_data, type_=Route, exclude_top_level_key=True)

        self.assert_proto_type_equal(openscenario_route, Route)

        start_waypoint = openscenario_route.waypoints[0]
        start_lane_position = start_waypoint.position.lanePosition
        self.assert_proto_type_equal(start_lane_position, LanePosition)

        self.assertEqual(start_lane_position.laneId, "22")
        self.assertEqual(start_lane_position.offset, 0.1750399287494411)
        self.assertEqual(start_lane_position.s, 35.714714923990464)
        self.assertEqual(start_lane_position.orientation.h, 2.883901414579166)

        end_waypoint = openscenario_route.waypoints[-1]
        end_lane_position = end_waypoint.position.lanePosition

        self.assertEqual(end_lane_position.laneId, "149")
        self.assertEqual(end_lane_position.offset, 1.4604610803960605)
        self.assertEqual(end_lane_position.s, 26.739416492972932)
        self.assertEqual(end_lane_position.orientation.h, -1.9883158777364047)

    def test_encoding_scenario_object(self):
        with open(self.scenario_object_file_path, 'r') as file:
            input = file.read()

        dict = yaml.safe_load(input)

        scenario_object = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict, type_=ScenarioObject, exclude_top_level_key=False)
        encoded_data = OpenScenarioEncoder.encode_proto_pyobject_to_yaml(
            scenario_object)

        decoded_data = yaml.safe_load(encoded_data)

        self.assertIsNotNone(decoded_data["ScenarioObject"])
        self.assertIsNotNone(decoded_data["ScenarioObject"]["Vehicle"])

    def test_encoding_openscenario_entities(self):
        with open(self.entities_file_path, 'r') as file:
            input = file.read()

        dict = yaml.safe_load(input)

        entities = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict, type_=Entities, exclude_top_level_key=True)
        encoded_data = OpenScenarioEncoder.encode_proto_pyobject_to_yaml(
            entities)

        decoded_data = yaml.safe_load(encoded_data)

        # TODO: Properties
        # assert dict == decoded_data

    def test_decoding_route(self):
        with open(self.route_file_path, 'r') as file:
            input = file.read()

        dict = yaml.safe_load(input)

        openscenario_route = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict, type_=Route, exclude_top_level_key=True)

        self.assert_proto_type_equal(openscenario_route, Route)

        start_waypoint = openscenario_route.waypoints[0]
        start_lane_position = start_waypoint.position.lanePosition
        self.assert_proto_type_equal(start_lane_position, LanePosition)

        self.assertEqual(start_lane_position.laneId, "22")
        self.assertEqual(start_lane_position.offset, 0.1750399287494411)
        self.assertEqual(start_lane_position.s, 35.714714923990464)
        self.assertEqual(start_lane_position.orientation.h, 2.883901414579166)

        end_waypoint = openscenario_route.waypoints[-1]
        end_lane_position = end_waypoint.position.lanePosition

        self.assertEqual(end_lane_position.laneId, "149")
        self.assertEqual(end_lane_position.offset, 1.4604610803960605)
        self.assertEqual(end_lane_position.s, 26.739416492972932)
        self.assertEqual(end_lane_position.orientation.h, -1.9883158777364047)

    def test_decoding_openscenario_object_controller(self):

        input = """
            ObjectController:
              Controller:
                name: ''
                Properties:
                  Property:
                    - name: isEgo
                      value: 'true'
        """

        dict = yaml.safe_load(input)

        object_controller = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict, type_=ObjectController, exclude_top_level_key=True)

        self.assert_proto_type_equal(object_controller, ObjectController)
        self.assert_object_controller(object_controller)

    def test_decoding_openscenario_vehicle(self):

        input = """
            Vehicle:
                name: ''
                vehicleCategory: car
                BoundingBox:
                  Center:
                    x: 1.355
                    y: 0
                    z: 1.25
                  Dimensions:
                    length: 4.77
                    width: 1.83
                    height: 2.5
                Performance:
                  maxSpeed: 50
                  maxAcceleration: INF
                  maxDeceleration: INF
                Axles:
                  FrontAxle:
                    maxSteering: 0.5236
                    wheelDiameter: 0.78
                    trackWidth: 1.63
                    positionX: 1.385
                    positionZ: 0.39
                  RearAxle:
                    maxSteering: 0.5236
                    wheelDiameter: 0.78
                    trackWidth: 1.63
                    positionX: 0
                    positionZ: 0.39
                Properties:
                  Property: []
        """

        dict = yaml.safe_load(input)

        vehicle = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict, type_=Vehicle, exclude_top_level_key=True)

        self.assert_proto_type_equal(vehicle, Vehicle)
        self.assert_vehicle(vehicle)

    def test_decoding_oneof_openscenario_entity_object(self):

        input = """
            Vehicle:
                name: ''
                vehicleCategory: car
                BoundingBox:
                  Center:
                    x: 1.355
                    y: 0
                    z: 1.25
                  Dimensions:
                    length: 4.77
                    width: 1.83
                    height: 2.5
                Performance:
                  maxSpeed: 50
                  maxAcceleration: INF
                  maxDeceleration: INF
                Axles:
                  FrontAxle:
                    maxSteering: 0.5236
                    wheelDiameter: 0.78
                    trackWidth: 1.63
                    positionX: 1.385
                    positionZ: 0.39
                  RearAxle:
                    maxSteering: 0.5236
                    wheelDiameter: 0.78
                    trackWidth: 1.63
                    positionX: 0
                    positionZ: 0.39
                Properties:
                  Property: []
        """

        dict = yaml.safe_load(input)

        entity_object = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict, type_=EntityObject, exclude_top_level_key=False)

        self.assertIsInstance(entity_object, EntityObject)
        self.assert_vehicle(entity_object.vehicle)

    def test_decoding_openscenario_scenario_object(self):
        with open(self.scenario_object_file_path, 'r') as file:
            input = file.read()

        dict = yaml.safe_load(input)

        scenario_object = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict, type_=ScenarioObject, exclude_top_level_key=False)

        self.assert_proto_type_equal(scenario_object, ScenarioObject)

        self.assert_vehicle(scenario_object.entityObject.vehicle)
        self.assert_object_controller(scenario_object.objectController)

    def test_decoding_openscenario_entities(self):
        with open(self.entities_file_path, 'r') as file:
            input = file.read()

        dict = yaml.safe_load(input)

        entities = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict, type_=Entities, exclude_top_level_key=True)
        self.assert_proto_type_equal(entities, Entities)
        self.assert_vehicle(entities.scenarioObjects[0].entityObject.vehicle)
        self.assert_object_controller(
            entities.scenarioObjects[0].objectController)

    def test_decoding_paramater_declarations(self):
        input = """
          ParameterDeclarations:
              ParameterDeclaration:
                - name: __ego_dimensions_length__
                  parameterType: double
                  value: '0'
                - name: __ego_dimensions_width__
                  parameterType: double
                  value: '0'
                - name: __ego_dimensions_height__
                  parameterType: double
                  value: '0'
                - name: __ego_center_x__
                  parameterType: double
                  value: '0'
                - name: __ego_center_y__
                  parameterType: double
                  value: '0'
                - name: __ego_center_z__
                  parameterType: double
                  value: '0'
        """

        dict = yaml.safe_load(input)

        parameter_declarations = OpenScenarioDecoder.decode_yaml_to_pyobject(
            yaml_dict=dict,
            type_=ParameterDeclarations,
            exclude_top_level_key=True)

        self.assertEqual(parameter_declarations.parameterDeclarations[0].name,
                         "__ego_dimensions_length__")
        self.assertEqual(
            parameter_declarations.parameterDeclarations[0].parameterType, 2)
        self.assertEqual(parameter_declarations.parameterDeclarations[1].name,
                         "__ego_dimensions_width__")
        self.assertEqual(
            parameter_declarations.parameterDeclarations[1].parameterType, 2)
        self.assertEqual(parameter_declarations.parameterDeclarations[1].value,
                         "0")
        self.assertEqual(parameter_declarations.parameterDeclarations[2].name,
                         "__ego_dimensions_height__")
        self.assertEqual(
            parameter_declarations.parameterDeclarations[2].parameterType, 2)
        self.assertEqual(parameter_declarations.parameterDeclarations[2].value,
                         "0")

    # Assertion methods

    def assert_object_controller(self, object_controller: ObjectController):
        self.assertEqual(object_controller.controller.name, "")
        self.assertEqual(
            object_controller.controller.properties.properties[0].name,
            "isEgo")
        self.assertEqual(
            object_controller.controller.properties.properties[0].value,
            "true")

    def assert_vehicle(self, vehicle):
        self.assertEqual(vehicle.vehicleCategory, Vehicle.Category.CAR)
        self.assertEqual(vehicle.boundingBox.center.x, 1.355)
        self.assertEqual(vehicle.boundingBox.dimensions.length, 4.77)
        self.assertEqual(vehicle.axles.frontAxle.maxSteering, 0.5236)

    def assert_proto_type_equal(self, reflection_type, pb2_type):
        self.assertEqual(str(reflection_type.__class__), str(pb2_type))
