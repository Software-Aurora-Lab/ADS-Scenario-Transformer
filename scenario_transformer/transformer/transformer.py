from abc import ABC, abstractmethod
from typing import TypeVar, Dict

Configuration = TypeVar('Configuration')
Source = TypeVar('Source')
Target = TypeVar('Target')


class Transformer(ABC):
    """
    Interface for defining Transformers for transforming Apollo Cyber Record Message to OpenSCENARIO Message.

    """
    configuration: Configuration

    @abstractmethod
    def transform(self, source: Source) -> Target:
        pass
