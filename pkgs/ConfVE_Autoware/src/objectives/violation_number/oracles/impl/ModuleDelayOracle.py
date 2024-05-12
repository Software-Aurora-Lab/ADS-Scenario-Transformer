from typing import List
from datetime import datetime
from src.objectives.violation_number.oracles.Violation import Violation
from src.objectives.violation_number.oracles.OracleInterface import OracleInterface
from src.tools.utils import get_real_time_from_msg


class ModuleDelayOracle(OracleInterface):
    """
    Module Delay Oracle is responsible for checking if the ADS's modules' delay exceeds
    2 seconds.
    Its features include:
        x:              float
        y:              float
        heading:        float
        speed:          float
        delay_module:   int
        delay_duration: float
    """

    MAX_DELAY = 0.5

    def __init__(self):
        self.modules = ['Localization', 'Perception', 'Planning']
        self.trackers = dict()
        self.started = {x: False for x in self.modules}
        for mod in self.modules:
            self.trackers[mod] = 0.0
        self.prev_t = None
        self.last_localization = None
        self.violations = list()

    def get_result(self):
        if self.last_localization is None:
            return list()

        # for t, m in zip(self.get_interested_topics(), self.modules):
        #     self.check_module_delay(m, 5.0)
        return self.violations

    def get_interested_topics(self) -> List[str]:
        return [
            '/localization/kinematic_state',
            '/perception/object_recognition/objects',
            '/planning/scenario_planning/trajectory'
        ]

    def check_module_delay(self, module_name: str, threshold: float):
        if self.trackers[module_name] > threshold:
            if self.last_localization is None:
                features = self.get_dummy_basic_info()
            else:
                features = self.get_basic_info_from_localization(self.last_localization)
            features['delay_module'] = self.modules.index(module_name)
            features['delay_duration'] = self.trackers[module_name]
            self.violations.append(
                Violation(
                    'ModuleDelayOracle',
                    features=features,
                    # key_label=str(module_name)
                    key_label = str(features['delay_duration'])
            )
            )
            return True
        return False

    def on_new_message(self, topic: str, message, t):
        t = get_real_time_from_msg(message.header)

        if self.prev_t is None:
            self.prev_t = t

        if topic == '/localization/kinematic_state':
            self.last_localization = message

        self.started[self.modules[self.get_interested_topics().index(topic)]] = True

        prev = datetime.fromtimestamp(self.prev_t / 1000000000)
        curr = datetime.fromtimestamp(t / 1000000000)
        dt = (curr - prev).total_seconds()
        self.prev_t = t

        for _t, m in zip(self.get_interested_topics(), self.modules):
            if not self.started[m]:
                continue

            self.trackers[m] += dt

            if topic == _t:
                # check if exceeds max
                if self.check_module_delay(m, ModuleDelayOracle.MAX_DELAY):
                    pass
                # reset
                self.trackers[m] = 0.0
