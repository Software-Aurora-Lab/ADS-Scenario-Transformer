import sqlite3
import os
import glob
from typing import Optional
from collections import defaultdict
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message


class ROSBagReader:

    def __init__(self, bag_dir_path: str):
        try:
            db3_path = self.first_file(directory=bag_dir_path, extension="db3")
        except:
            raise Exception("Invalid record format")

        self.sql_connection = sqlite3.connect(db3_path)
        self.sql_cursor = self.sql_connection.cursor()
        self.db3_path = db3_path

        ## create a message type map
        topics_data = self.sql_cursor.execute("SELECT id, name, type FROM topics").fetchall()
        self.topic_type = {name_of: type_of for id_of, name_of, type_of in topics_data}
        self.topic_id = {name_of: id_of for id_of, name_of, type_of in topics_data}
        self.topic_msg_message = {name_of: get_message(type_of) for id_of, name_of, type_of in topics_data}

        self.fetch_all_msgs_sql = "select topics.name as topic, data as message, timestamp as t from messages join topics on messages.topic_id = topics.id order by timestamp"

        unique_topic = set(list(self.topic_id.keys()))
        self.grouped_topic = defaultdict(list)

        for topic in unique_topic:
            splited = topic.split('/')
            self.grouped_topic[splited[1]].append(topic)

    def first_file(self, directory: str, extension: str) -> Optional[str]:
        pattern = os.path.join(directory, f'*.{extension}')
        files = glob.glob(pattern)
        return files[0]

    def read_messages(self):
        rows = self.sql_cursor.execute(self.fetch_all_msgs_sql).fetchall()
        return rows

    def deserialize_msg(self, data, topic_name):
        return deserialize_message(data, self.topic_msg_message[topic_name])

    def __del__(self):
        self.sql_connection.close()

    def read_specific_messages(self, topic_name: str):
        topic_data_list = []
        for topic, message, t in self.read_messages():
            # if topic == topic_name:
            if topic_name in topic:

                msg = self.deserialize_msg(message, topic)
                topic_data_list.append((topic, msg, t))
        return topic_data_list


    def get_messages(self, topic_name: str):
        topic_id = self.topic_id[topic_name]
        rows = self.sql_cursor.execute("SELECT timestamp, data FROM messages WHERE topic_id = {}".format(topic_id)).fetchall()
        print(type(rows[0][0]), type(rows[0][1])) 
        return [(timestamp, deserialize_message(data, self.topic_msg_message[topic_name])) for timestamp, data in rows]
