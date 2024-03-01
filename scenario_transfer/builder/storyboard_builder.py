from openscenario_msgs import Storyboard
from scenario_transfer.builder import Builder


class StoryboardBuilder(Builder):

    product: Storyboard

    def __init__(self):
        pass

    def make_stories(self):
        pass

    def make_stop_trigger(self):
        pass

    def get_result(self) -> Storyboard:
        return Storyboard()


# // Message for Init
# message Init {
#     required InitActions actions = 1;  // 1..1
# }

# // Message for InitActions
# message InitActions {
#     repeated GlobalAction globalActions = 1;   // 0..*
#     repeated UserDefinedAction userDefinedActions = 2;  // 0..*
#     repeated Private privates = 3;             // 0..*
# }
# // Message for Storyboard
# message Storyboard {
#     required Init init = 1;  // 1..1
#     repeated Story stories = 2;  // 1..*
#     required Trigger stopTrigger = 3;  // 1..1
# }
