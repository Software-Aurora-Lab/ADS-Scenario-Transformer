from typing import List
from openscenario_msgs import Act, Trigger, ManeuverGroup
from scenario_transfer.builder import Builder


class ActBuilder(Builder):
    product: Act

    def __init__(self, name: str = ""):
        self.name = name
        self.start_trigger = None
        self.stop_trigger = None

    def make_maneuver_groups(self, maneuver_groups: List[ManeuverGroup]):
        self.maneuver_groups = maneuver_groups

    def make_start_trigger(self, trigger: Trigger):
        self.start_trigger = trigger

    def make_stop_trigger(self, trigger: Trigger):
        self.stop_trigger = trigger

    def get_result(self) -> Act:
        assert len(
            self.maneuver_groups) > 0, "Act needs at least one maneuver group"
        assert self.start_trigger is not None

        if self.stop_trigger:
            self.product = Act(name=self.name,
                               maneuverGroups=self.maneuver_groups,
                               startTrigger=self.start_trigger,
                               stopTrigger=self.stop_trigger)
        else:
            self.product = Act(name=self.name,
                               maneuverGroups=self.maneuver_groups,
                               startTrigger=self.start_trigger)
        return self.product
