from typing import List
from openscenario_msgs import Storyboard, Init, Story, StopTrigger
from ads_scenario_transformer.builder import Builder


class StoryboardBuilder(Builder):
    product: Storyboard

    def __init__(self):
        self.stories = []

    def make_init(self, init: Init):
        self.init = init

    def make_stories(self, stories: List[Story]):
        self.stories = stories

    def make_stop_trigger(self, trigger: StopTrigger):
        self.stop_trigger = trigger

    def get_result(self) -> Storyboard:
        assert self.stop_trigger is not None

        self.product = Storyboard(init=self.init,
                                  stories=self.stories,
                                  stopTrigger=self.stop_trigger)
        return self.product
