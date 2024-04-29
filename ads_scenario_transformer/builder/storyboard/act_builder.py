from typing import List
from openscenario_msgs import Act, StartTrigger, StopTrigger, ManeuverGroup
from ads_scenario_transformer.builder import Builder


class ActBuilder(Builder):
    product: Act

    def __init__(self, name: str = ""):
        self.name = name
        self.start_trigger = None
        self.stop_trigger = None

    def make_maneuver_groups(self, maneuver_groups: List[ManeuverGroup]):
        self.maneuver_groups = maneuver_groups

    def make_start_trigger(self, trigger: StartTrigger):
        self.start_trigger = trigger

    def make_stop_trigger(self, trigger: StopTrigger):
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
