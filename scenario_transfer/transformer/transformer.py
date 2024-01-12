from abc import ABC, abstractmethod
from typing import TypeVar, Dict

Source = TypeVar('Source')
Target = TypeVar('Target')


class Transformer(ABC):
    """
    Interface for defining Transformers for transforming Apollo Cyber Record Message to OpenSCENARIO Message.

    Properties:
        properties (Dict[Any]): Dict of properties for transforming source object to target one.
    """
    properties: Dict

    @abstractmethod
    def transform(self, source: Source) -> Target:
        pass
