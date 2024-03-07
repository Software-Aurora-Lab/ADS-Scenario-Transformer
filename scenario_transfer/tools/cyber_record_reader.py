from enum import Enum
import base64
import math
from protobuf_to_dict import protobuf_to_dict
from cyber_record.record import Record

class CyberRecordChannel(Enum):
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

class CyberRecordReader:

    @staticmethod
    def read_channel(source_path: str, channel: CyberRecordChannel, max_count=float('inf')):
        record = Record(source_path)
        messages = record.read_messages(channel.value)
        result = []
        count = 0
        
        for topic, message, t in messages:
            if count > max_count:
                break
            result.append(message)
            count += 1
        return result

    @staticmethod
    def read_all_channels(source_path: str, maxCount=float('inf')):
        """
        Read all target channels
        """
        return [self.read_channel(source_path=source_path, channel=channel, maxCount=maxCount) for channel in CyberRecordChannel]
        