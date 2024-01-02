import yaml
from protobuf_to_dict import protobuf_to_dict


class FormatTransformer:

    @staticmethod
    def transform_proto_pyobject_to_yaml(proto_pyobject):
        proto_dict = protobuf_to_dict(proto_pyobject, use_enum_labels=True)

        toplevel_name_included_dict = {
            type(proto_pyobject).__name__: proto_dict
        }
        result_dict = FormatTransformer.convert_to_compatible_element(
            toplevel_name_included_dict)

        yaml_data = yaml.dump(result_dict, default_flow_style=False)
        return yaml_data

    @staticmethod
    def to_camel(snake):
        first, *others = snake.split('_')
        return ''.join([first.lower(), *map(str.title, others)])

    @staticmethod
    def to_pascal(snake):
        if '_' not in snake:
            return snake
        return ''.join(word.capitalize() for word in snake.split('_'))

    @staticmethod
    def convert_to_compatible_element(input_dict):
        res_dict = {}
        for key, value in input_dict.items():
            new_key = FormatTransformer.to_camel(key)
            new_value = value
            if isinstance(value, dict):
                new_key = FormatTransformer.to_pascal(key)
                new_value = FormatTransformer.convert_to_compatible_element(
                    value)
            elif isinstance(value, list):
                new_key = FormatTransformer.to_pascal(key)
                new_value = [
                    FormatTransformer.convert_to_compatible_element(item)
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
