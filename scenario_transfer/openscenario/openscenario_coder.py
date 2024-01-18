import yaml
import difflib
from typing import Optional, TypeVar, Dict, Type

from protobuf_to_dict import protobuf_to_dict
from google.protobuf.descriptor import Descriptor

from scenario_transfer.openscenario.openscenario_attributes_name_mapper import OpenScenarioAttributesNameMapper


class OpenScenarioEncoder:

    @staticmethod
    def encode_proto_pyobject_to_yaml(proto_pyobject):
        proto_dict = protobuf_to_dict(proto_pyobject, use_enum_labels=True)

        toplevel_name_included_dict = {
            type(proto_pyobject).__name__: proto_dict
        }

        name_dict = OpenScenarioAttributesNameMapper().parse_definition()

        result_dict = OpenScenarioEncoder.convert_to_compatible_element(
            toplevel_name_included_dict, name_dict,
            type(proto_pyobject).__name__)

        yaml_data = yaml.dump(result_dict, default_flow_style=False)
        return yaml_data

    @staticmethod
    def convert_to_compatible_element(input_dict, name_dict, root_type_name):
        res_dict = {}
        for key, value in input_dict.items():
            matches = difflib.get_close_matches(key, name_dict[root_type_name])

            new_key = key if len(matches) == 0 else matches[0]
            new_value = value
            if isinstance(value, dict):
                new_value = OpenScenarioEncoder.convert_to_compatible_element(
                    value, name_dict, new_key)
            elif isinstance(value, list):
                new_value = [
                    OpenScenarioEncoder.convert_to_compatible_element(
                        item, name_dict, new_key)
                    if isinstance(item, dict) else item for item in value
                ]
            elif isinstance(value, str):
                if '_' in value:  # enum value
                    new_value = value.split('_')[-1].lower()
                else:
                    new_value = value
            else:
                new_value = value
            res_dict[new_key] = new_value
        return res_dict


class OpenScenarioDecoder:

    T = TypeVar('T')

    @staticmethod
    def decode_yaml_to_pyobject(yaml_dict: Dict, type_: Type[T],
                                exclude_top_level_key: bool) -> T:
        name_dict = OpenScenarioDecoder.get_all_fields_name(type_)
        data_dict = OpenScenarioDecoder.convert_to_compatible_element(
            yaml_dict, name_dict, type_.__name__)

        if exclude_top_level_key:
            data_dict = data_dict[list(data_dict.keys())[0]]

        return type_(**data_dict)

    @staticmethod
    def get_all_fields_name(protobuf_type) -> dict:
        """
        Recursively get all fields name of a protobuf type. Values are saved based on below rules.

        Object
        - Type: List[(field_name, field_type)])]
        - Example: {'Route': [('closed', 8), ('name', 9), ('parameter_declarations', 'ParameterDeclaration'), ('waypoints', 'Waypoint')]}

        Enum
        - Type: Dict[field_name: Dict[openscenario_applicable_name, original_name]]]
        - Example: {'route_strategy': {'FASTEST': 'ROUTESTRATEGY_FASTEST', 'LEAST_INTERSECTIONS': 'ROUTESTRATEGY_LEAST_INTERSECTIONS', 'RANDOM': 'ROUTESTRATEGY_RANDOM', 'SHORTEST': 'ROUTESTRATEGY_SHORTEST'}}
        
        """

        message_descriptor = protobuf_type
        if not isinstance(protobuf_type, Descriptor):
            message_descriptor = protobuf_type.DESCRIPTOR

        key = message_descriptor.name
        attributes_names = {}

        if len(message_descriptor.fields) != 0:
            attributes_names = {key: []}

        for field_descriptor in message_descriptor.fields:
            if field_descriptor.message_type:
                attributes_names[key].append(
                    (field_descriptor.name,
                     field_descriptor.message_type.name))
                sub_dict = OpenScenarioDecoder.get_all_fields_name(
                    field_descriptor.message_type)
                attributes_names |= sub_dict
            elif field_descriptor.enum_type:
                typename = field_descriptor.enum_type.name.upper()
                enum_name_map = {}
                for enum_value_descriptor in field_descriptor.enum_type.values:
                    if enum_value_descriptor.name.startswith(typename):
                        saved_value = enum_value_descriptor.name[len(typename
                                                                     ) + 1:]
                        enum_name_map[saved_value] = enum_value_descriptor.name

                attributes_names[key].append(
                    {field_descriptor.name: enum_name_map})
            else:
                attributes_names[key].append(
                    (field_descriptor.name, field_descriptor.type))

        return attributes_names

    @staticmethod
    def decode_enum(name_dict, root_type_name, target: str) -> Optional[str]:
        """
        Decode enum value from yaml to original name.
        e.g. If root_type_name is ROUTESTRATEGY and target is fastest, it returns ROUTESTRATEGY_FASTEST
        
        """
        for pair in name_dict[root_type_name]:
            if isinstance(pair, dict):
                typename = list(pair.keys())[0]
                if target.upper() in pair[typename].keys():
                    return pair[typename][target.upper()]
        return None

    @staticmethod
    def convert_to_compatible_element(input_dict, name_dict, root_type_name):
        """
        Convert key of a dictionary to a compatible one which enable initializing object.
        
        """

        @staticmethod
        def create_key(name_dict, key, root_name) -> str:

            attr_names = []
            for x in name_dict[root_type_name]:
                if isinstance(x, tuple):
                    attr_names.append(x[0])
                else:
                    attr_names.append(list(x.keys())[0])  # enum hanldling

            matches = difflib.get_close_matches(key, attr_names)
            return matches[0] if matches else key

        res_dict = {}
        for key, value in input_dict.items():
            new_key = create_key(name_dict, key, root_type_name)
            new_value = value
            if isinstance(value, dict):
                new_value = OpenScenarioDecoder.convert_to_compatible_element(
                    value, name_dict, key)
            elif isinstance(value, list):
                new_value = [
                    OpenScenarioDecoder.convert_to_compatible_element(
                        item, name_dict, key)
                    if isinstance(item, dict) else item for item in value
                ]
            elif isinstance(value, str):
                decoded_enum = OpenScenarioDecoder.decode_enum(
                    name_dict, root_type_name, value)
                if decoded_enum:
                    new_value = decoded_enum
                else:
                    new_value = value
            else:
                new_value = value
            res_dict[new_key] = new_value
        return res_dict
