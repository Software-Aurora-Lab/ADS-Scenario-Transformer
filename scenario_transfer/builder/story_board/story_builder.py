from typing import List
from openscenario_msgs import Story, Act, ParameterDeclaration
from scenario_transfer import Builder


class StoryBuilder(Builder):
    product: Story

    def __init__(self,
                 name: str = "",
                 parameter_declarations: List[ParameterDeclaration] = []):
        self.name = name
        self.parameter_declarations = parameter_declarations

    def make_acts(self, acts: List[Act]):
        self.product = Story(name=self.name,
                             parameterDeclarations=self.parameter_declarations,
                             acts=acts)

    def get_result(self) -> Story:
        assert len(self.product.acts) > 0, "Story needs at least one act"

        return self.product
