from enum import Enum
from typing import Optional
from pathlib import Path
import yaml
import json
import base64
import math

from protobuf_to_dict import protobuf_to_dict
from cyber_record.record import Record

class CyberRecordReader:

    class TargetChannels(Enum):
        PERCEPTION_OBSTACLES = "/apollo/perception/obstacles"
        ROUTING_REQUEST = "/apollo/routing_request"
        TRAFFIC_LIGHT = "/apollo/perception/traffic_light"
        MONITOR = "/apollo/monitor"
        ROUTING_RESPONSE = "/apollo/routing_response"
        ROUTING_RESPONSE_HISTORY = "/apollo/routing_response_history"
        PLANNING = "/apollo/planning"
        LEARNING_DATA = "/apollo/planning/learning_data"
        PREDICTION = "/apollo/prediction"
        PREDICTION_PERCEPTION_OBSTACLES = "/apollo/prediction/perception_obstacles"
        LOCALIZATION_POSE = "/apollo/localization/pose"
        CANBUS_CHASSIS = "/apollo/canbus/chassis"

    def read_channel(self, source_path: str, channel: TargetChannels):
        record = Record(source_path)
        messages = record.read_messages(channel.value)
        result = []
        for topic, message, t in messages:
            result.append(protobuf_to_dict(message, use_enum_labels=True))
        
        py_dict = {channel.name: result}
        decoded_dict = self.decode_binary(py_dict)
        yaml_data = yaml.dump(decoded_dict, default_flow_style=False)

        src_path = Path(source_path)
        file_name = f"{src_path.name}_{channel.name.lower()}"

        with open(f"{src_path.parent}/yaml/{file_name}.yaml", "w") as file:
            file.write(yaml_data)
            print(f"Updated to {src_path.parent}/yaml/{file_name}.yaml")
        with open(f"{src_path.parent}/json/{file_name}.json", "w") as file:
            json.dump(decoded_dict, file, indent=2)
            print(f"Updated to {src_path.parent}/json/{file_name}.json")

    def read_all_channels(self, file_path: str):
        """
        Read all target channels
        """
        for channel in CyberRecordReader.TargetChannels:
            self.read_channel(source_path=file_path, channel=channel)            

    def decode_binary(self, value):
        """
        Recursively decode bytes into utf-8 values
        """
        if isinstance(value, bytes):
            try:
                decoded_value = value.decode("utf-8")
                return decoded_value
            except base64.binascii.Error:
                return value
        elif isinstance(value, list):
            return [self.decode_binary(item) for item in value]
        elif isinstance(value, dict):
            return {key: self.decode_binary(sub_value) for key, sub_value in value.items()}
        elif isinstance(value, float) and math.isnan(value):
            return 0.0
        else:
            return value