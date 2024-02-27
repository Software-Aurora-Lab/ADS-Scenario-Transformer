from openscenario_msgs import Storyboard
from scenario_transfer.builder import Builder


class StoryboardBuilder(Builder):

    def __init__(self):
        pass

    def get_result(self) -> Storyboard:
        return Storyboard()
