from abc import ABC, abstractmethod
from typing import TypeVar, List

T = TypeVar('T')
V = TypeVar('V')


class Transformable(ABC):
    properties: List

    @abstractmethod
    def transform(self, source: T) -> V:
        pass
