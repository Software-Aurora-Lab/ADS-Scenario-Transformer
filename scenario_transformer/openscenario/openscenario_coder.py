import yaml
import re
from typing import Optional, TypeVar, Dict, Type, Tuple, List
import os
import importlib
from protobuf_to_dict import protobuf_to_dict
from google.protobuf.descriptor import Descriptor
from definitions import PROJECT_ROOT


class OpenScenarioCoder:
    field_name_cache = {}
    openscenario_msgs_path = PROJECT_ROOT + "/openscenario_msgs"

    @staticmethod
    def update_field_names_in_proto_files(
            openscenario_protobuf_directory: str = openscenario_msgs_path):

        if OpenScenarioCoder.field_name_cache:
            return

        proto_files = [
            file for file in os.listdir(openscenario_protobuf_directory)
            if file.endswith(".proto")
        ]

        for proto_file in proto_files:
            module_name = proto_file.replace(".proto", "_pb2")
            try:
                package_module = importlib.import_module(module_name)
                field_names = OpenScenarioCoder.list_field_names_in_protobuf_package(
                    package_module)
                OpenScenarioCoder.field_name_cache.update(field_names)
            except ImportError as e:
                print(f"Failed to import {module_name}: {e}")

    @staticmethod
    def list_field_names_in_protobuf_package(package_module):
        results = {}
        for obj_name in dir(package_module):
            obj = getattr(package_module, obj_name)

            if isinstance(obj, Descriptor):
                fields = []
                for field_descriptor in obj.fields:
                    if field_descriptor.message_type:
                        fields.append((field_descriptor.name,
                                       field_descriptor.message_type.name))

                    elif field_descriptor.enum_type:
                        typename = field_descriptor.enum_type.name.upper()
                        enum_name_map = {}
                        for enum_value_descriptor in field_descriptor.enum_type.values:
                            defined_name = enum_value_descriptor.name
                            if defined_name.startswith(typename):
                                saved_value = defined_name[len(typename) + 1:]
                                enum_name_map[saved_value] = defined_name
                            else:
                                enum_name_map[defined_name] = defined_name
                        fields.append((field_descriptor.name, enum_name_map))
                    else:
                        fields.append(
                            (field_descriptor.name, field_descriptor.type))

                results[obj.name] = fields

        return results

    @staticmethod
    def is_oneof_type_or_skipped_type(type_name) -> bool:
        one_of_type = [
            "StoryboardElement",
            "CatalogElement",
            "Entity",
            "EntityObject",
        ]
        skipped_type = ["PrivateAction"]
        return type_name in one_of_type or type_name in skipped_type

    plural_singular_types = {
        "Properties": "Property",
        "ScenarioModifiers": "ScenarioModifier",
        "CatalogLocations": "CatalogLocation",
        "TrafficSignals": "TrafficSignalController",
        "ParameterDeclarations": "ParameterDeclaration"
    }

    @staticmethod
    def is_plural_type(type_name) -> bool:
        return type_name in OpenScenarioCoder.plural_singular_types.keys()


class OpenScenarioEncoder:

    including_default_value_fields = {
        "Actors": [("EntityRef", [])],
        "StopTrigger": [("ConditionGroup", [])]
    }

    @staticmethod
    def encode_proto_pyobject_to_dict(proto_pyobject,
                                      wrap_result_with_typename=True):
        proto_dict = protobuf_to_dict(proto_pyobject, use_enum_labels=True)

        OpenScenarioCoder.update_field_names_in_proto_files()

        result_dict = OpenScenarioEncoder.convert_to_compatible_element(
            input_dict=proto_dict,
            name_dict=OpenScenarioCoder.field_name_cache,
            root_type_name=type(proto_pyobject).__name__)

        if wrap_result_with_typename:
            result_dict = {type(proto_pyobject).__name__: result_dict}

        return result_dict

    @staticmethod
    def encode_proto_pyobject_to_yaml(proto_pyobject,
                                      wrap_result_with_typename=True):

        result_dict = OpenScenarioEncoder.encode_proto_pyobject_to_dict(
            proto_pyobject, wrap_result_with_typename)

        yaml_data = yaml.dump(result_dict,
                              sort_keys=False,
                              default_flow_style=False)

        return yaml_data

    @staticmethod
    def convert_to_compatible_element(input_dict, name_dict, root_type_name):

        def snake_to_camel(snake_str) -> str:
            words = snake_str.lower().split('_')
            return words[0] + ''.join(word.title() for word in words[1:])
        
        def search_type_name(field_name: str,
                             root_type_name: str) -> Optional[str]:
            for field_name_key, type_name in name_dict[root_type_name]:
                if field_name == field_name_key:
                    return type_name
            return None

        res_dict = {}
        for key, value in input_dict.items():

            type_name = search_type_name(field_name=key,
                                         root_type_name=root_type_name)

            new_key = key
            new_value = value

            if isinstance(type_name, str):
                # object
                new_key = type_name

                if isinstance(value, dict):
                    if OpenScenarioCoder.is_oneof_type_or_skipped_type(
                            type_name):
                        # unwrap dictionary
                        for k, t in name_dict[type_name]:
                            if k == list(value.keys())[0]:
                                new_key = t
                                new_value = value[k]
                                break
                        new_value = OpenScenarioEncoder.convert_to_compatible_element(
                            new_value, name_dict, new_key)
                    elif OpenScenarioCoder.is_plural_type(
                            type_name) and value == {}:

                        sub_key = OpenScenarioCoder.plural_singular_types[
                            type_name]
                        new_value = {sub_key: []}
                    elif type_name in OpenScenarioEncoder.including_default_value_fields:
                        fields = OpenScenarioEncoder.including_default_value_fields[
                            type_name]
                        for (field, default_value) in fields:
                            if field not in value:
                                new_value[field] = default_value
                        new_value = OpenScenarioEncoder.convert_to_compatible_element(
                            new_value, name_dict, new_key)
                    else:
                        new_value = OpenScenarioEncoder.convert_to_compatible_element(
                            value, name_dict, new_key)
                elif isinstance(value, list):
                    new_value = [
                        OpenScenarioEncoder.convert_to_compatible_element(
                            input_dict=item,
                            name_dict=name_dict,
                            root_type_name=new_key) for item in value
                    ]
            elif isinstance(type_name, dict):
                # enum
                for enum_key, enum_value in type_name.items():
                    if value == enum_value:
                        new_value = snake_to_camel(enum_key)
                        break

            if new_value == float('inf'):
                new_value = 'INF'

            res_dict[new_key] = new_value
        return res_dict


class OpenScenarioDecoder:
    T = TypeVar('T')

    @staticmethod
    def decode_yaml_to_pyobject(yaml_dict: Dict, type_: Type[T],
                                exclude_top_level_key: bool) -> T:

        OpenScenarioCoder.update_field_names_in_proto_files()

        if exclude_top_level_key:
            yaml_dict = yaml_dict[list(yaml_dict.keys())[0]]

        data_dict = OpenScenarioDecoder.convert_to_compatible_element(
            input_dict=yaml_dict,
            name_dict=OpenScenarioCoder.field_name_cache,
            root_type_name=type_.__name__,
            parent_type_name="")

        return type_(**data_dict)

    @staticmethod
    def decode_enum(name_dict, root_type_name, target: str) -> Optional[str]:
        """
        Decode enum value from yaml to original name.
        e.g. If root_type_name is ROUTESTRATEGY and target is fastest, it returns ROUTESTRATEGY_FASTEST
        
        """

        if target == "":
            return None

        res = None
        # change camel case to snake case
        enum_key = re.sub(r'(?<!^)(?=[A-Z])', '_', target).upper()
        for pair in name_dict[root_type_name]:
            if isinstance(pair[1], dict):
                enum_map = pair[1]
                if enum_key in enum_map.keys():
                    res = enum_map[enum_key]
                    break
        return res

    @staticmethod
    def is_enum(name_dict, root_type_name, key) -> bool:
        for k, t in name_dict[root_type_name]:
            if k == key and isinstance(t, dict):
                return True
        return False

    @staticmethod
    def convert_to_compatible_element(input_dict,
                                      name_dict,
                                      root_type_name,
                                      parent_type_name=""):
        """
        Convert key of a dictionary to a compatible one which enable initializing object.
        
        """

        @staticmethod
        def search_pyobject_field_name(name_dict, key, root_name) -> str:
            res = key
            for field_name, type_name in name_dict[root_name]:
                if type_name == key or field_name.lower() == key.lower():
                    if isinstance(type_name, str):
                        res = field_name
                        break

            return res

        @staticmethod
        def search_oneof(
                searching_type_name: str,
                type_pair: Dict[str, str]) -> Optional[Tuple[str, str, str]]:

            for field_name, type_name in type_pair:
                if OpenScenarioCoder.is_oneof_type_or_skipped_type(type_name):
                    one_of_wrapper_field = field_name

                    for one_of_field, one_of_type_name in name_dict[type_name]:
                        if one_of_type_name == searching_type_name:
                            return (one_of_wrapper_field, one_of_field,
                                    one_of_type_name)

            return None

        @staticmethod
        def search_field_name(type_name: str,
                              root_type_name: str) -> Optional[str]:
            for field_name, type_name_key in name_dict[root_type_name]:
                if type_name == type_name_key:
                    return field_name
            return None

        # Code starts here
        res_dict = {}

        if parent_type_name == "":
            parent_type_name = root_type_name

        if root_type_name == "":
            return input_dict

        for key, value in input_dict.items():
            new_key = search_pyobject_field_name(name_dict, key,
                                                 root_type_name)
            new_value = value

            # find type information
            new_root_type_name = ""
            one_of_wrapper_field = ""
            one_of_field_name = ""
            for field_name, type_name in name_dict[root_type_name]:
                if new_key == field_name:
                    new_root_type_name = type_name
                    break

                one_of_result = search_oneof(
                    searching_type_name=new_key,
                    type_pair=name_dict[root_type_name])
                if one_of_result:
                    one_of_wrapper_field = one_of_result[0]
                    one_of_field_name = one_of_result[1]
                    new_root_type_name = one_of_result[2]
                    break

            if new_root_type_name == "":
                if isinstance(parent_type_name, str):
                    one_of_result = search_oneof(
                        searching_type_name=new_key,
                        type_pair=name_dict[parent_type_name])
                    if one_of_result:
                        one_of_wrapper_field = one_of_result[0]
                        one_of_field_name = one_of_result[1]
                        new_root_type_name = one_of_result[2]

            if isinstance(value, dict):
                new_value = OpenScenarioDecoder.convert_to_compatible_element(
                    input_dict=value,
                    name_dict=name_dict,
                    root_type_name=new_root_type_name,
                    parent_type_name=root_type_name)

                # wrap one_of type
                if one_of_wrapper_field != "":
                    new_value = {one_of_field_name: new_value}
                    res_dict[one_of_wrapper_field] = new_value
                else:
                    res_dict[new_key] = new_value

            elif isinstance(value, list):

                new_value = [
                    OpenScenarioDecoder.convert_to_compatible_element(
                        input_dict=value_element,
                        name_dict=name_dict,
                        root_type_name=new_root_type_name,
                        parent_type_name=root_type_name)
                    for value_element in value
                ]
                field_name = search_field_name(type_name=new_key,
                                               root_type_name=root_type_name)
                if field_name:
                    res_dict[field_name] = new_value
                else:
                    res_dict[new_key] = new_value
            elif isinstance(value, str):
                # enum + string value
                if OpenScenarioDecoder.is_enum(name_dict, root_type_name, key):
                    decoded_enum = OpenScenarioDecoder.decode_enum(
                        name_dict, root_type_name, value)
                    new_value = decoded_enum
                else:
                    if value.upper() == 'INF':
                        value = float('inf')
                    new_value = value
                res_dict[new_key] = new_value
            else:
                new_value = value
                res_dict[new_key] = new_value

        return res_dict
