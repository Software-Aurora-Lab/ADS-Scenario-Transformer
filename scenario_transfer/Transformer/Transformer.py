from abc import ABC, abstractmethod
from typing import TypeVar, List

Source = TypeVar('Source')
Target = TypeVar('Target')


class Transformer(ABC):
    """
    Interface for defining Transformers for transforming Apollo Cyber Record Message to OpenSCENARIO Message.

    Properties:
        properties (list[Any]): List of properties for transforming source object to target one.
    """
    properties: List

    @abstractmethod
    def transform(self, source: Source) -> Target:
        pass
