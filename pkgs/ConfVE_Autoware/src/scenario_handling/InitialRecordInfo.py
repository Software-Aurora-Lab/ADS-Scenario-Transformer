
class InitialRecordInfo:

    def __init__(self, is_record_file, record_id, record_name, record_file_path, map_name):
        self.is_record_file = is_record_file
        self.record_name = record_name
        self.record_id = record_id
        self.record_file_path = record_file_path
        self.map_name = map_name

        self.violation_results = []
        self.violation_num = 0

        self.routing_request = None
        self.obs_perception_list = []
        self.traffic_lights_list = []

        self.finished_rerun = False

        self.coord = None
        self.heading = None

    def update_violation_directly(self, violation_results):
        self.violation_results = violation_results
        self.violation_num = len(violation_results)
