from typing import List
from openscenario_msgs import ParameterDeclarations, ParameterDeclaration, ParameterType
from ads_scenario_transformer.builder import Builder


class ParameterDeclarationsBuilder(Builder):

    product: ParameterDeclarations

    def __init__(self, parameterDeclarations: List[ParameterDeclaration]):
        self.product = ParameterDeclarations(
            parameterDeclarations=parameterDeclarations)

    def get_result(self) -> ParameterDeclarations:
        return self.product


class ParameterDeclarationBuilder(Builder):

    product: ParameterDeclaration

    def __init__(self, name: str, type: ParameterType, value: str):
        self.product = ParameterDeclaration(name, type, value)

    def get_result(self) -> ParameterDeclaration:
        return self.product
