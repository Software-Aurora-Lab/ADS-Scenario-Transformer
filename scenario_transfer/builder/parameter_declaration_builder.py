from openscenario_msgs import ParameterDeclaration
from scenario_transfer.builder import Builder


class ParameterDeclarationBuilder(Builder):

    def __init__(self):
        pass

    def get_result(self) -> ParameterDeclaration:
        return ParameterDeclaration()
