import pandas
from scenario_handling.InitialRecordInfo import InitialRecordInfo
from src.config import ADS_SCENARIO_DIR, PROJECT_ROOT, MAP_NAME


class MessageGenerator:
    def __init__(self):
        self.scenario_dir_path = ADS_SCENARIO_DIR
        self.scenario_record_path_list = []
        self.scenario_recordname_list = []
        self.scenario_map_name_list = []
        self.total_records_count = 0
        self.pre_record_info_list = []
        self.violation_results_list = []
        self.violation_num_list = []
        self.record_counter = 0
        self.get_record_path_list()

    def get_record_path_list(self):
        csv_fle = pandas.read_csv(f"{PROJECT_ROOT}/data/scenario_ranking/{MAP_NAME}.csv")
        scenario_recordname_list = list(csv_fle["scenario_record_name"])
        map_name_list = list(csv_fle["map_name"])
        self.scenario_record_path_list = [f"{self.scenario_dir_path}/{recordname}.yaml" for recordname in
                                          scenario_recordname_list]
        self.total_records_count = len(self.scenario_record_path_list)
        self.scenario_recordname_list = scenario_recordname_list
        self.scenario_map_name_list = map_name_list

    def update_total_violation_results(self):
        self.violation_results_list = [pri.violation_results for pri in self.pre_record_info_list]
        self.violation_num_list = [len(vr) for vr in self.violation_results_list]
        print("Records Info:")
        print(self.violation_num_list)

    def update_selected_records_violatioin_directly(self, violation_results_list_with_sid):
        for sid, violation_results in violation_results_list_with_sid:
            for i in range(len(self.pre_record_info_list)):
                if sid == self.pre_record_info_list[i].record_id:
                    self.pre_record_info_list[i].update_violation_directly(violation_results)
        self.update_total_violation_results()
        self.update_rerun_status()

    def replace_records(self, replaced_id_list):
        print("----------")
        print(f"Replacing Record List: {replaced_id_list}")
        print("----------")
        for rid in replaced_id_list:
            if len(self.scenario_record_path_list) > self.record_counter:
                print(f"Replacing Record_{rid}...")
                for i in range(len(self.pre_record_info_list)):
                    if rid == self.pre_record_info_list[i].record_id:
                        pre_record_info = InitialRecordInfo(True, self.record_counter,
                                                            self.scenario_recordname_list[self.record_counter],
                                                            self.scenario_record_path_list[self.record_counter],
                                                            self.scenario_map_name_list[self.record_counter])
                        self.record_counter += 1
                        self.pre_record_info_list[i] = pre_record_info
        self.update_total_violation_results()

    def replace_record(self, rid):
        if len(self.scenario_record_path_list) > self.record_counter:
            print(f"Replacing Record_{rid}...")
            for i in range(len(self.pre_record_info_list)):
                if rid == self.pre_record_info_list[i].record_id:
                    pre_record_info = InitialRecordInfo(True, self.record_counter,
                                                        self.scenario_recordname_list[self.record_counter],
                                                        self.scenario_record_path_list[self.record_counter],
                                                        self.scenario_map_name_list[self.record_counter])
                    self.record_counter += 1
                    self.pre_record_info_list[i] = pre_record_info
                    return pre_record_info
        # return pre_record_info

    def update_rerun_status(self):
        for p in self.pre_record_info_list:
            p.finished_rerun = True

    def get_not_rerun_record(self):
        return [p for p in self.pre_record_info_list if not p.finished_rerun]

    def get_record_info_by_record_id(self, record_id_list):
        for record_id in record_id_list:
            pre_record_info = InitialRecordInfo(True, record_id,
                                                self.scenario_recordname_list[record_id],
                                                self.scenario_record_path_list[record_id],
                                                self.scenario_map_name_list[record_id])
            self.pre_record_info_list.append(pre_record_info)
        self.update_total_violation_results()
        self.record_counter = max(record_id_list) + 1
