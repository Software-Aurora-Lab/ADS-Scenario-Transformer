from abc import ABC, abstractmethod
from typing import Type, TypeVar, List

T = TypeVar('T')
V = TypeVar('V')
X = TypeVar('X')

class Transformable(ABC):
    properties: List

    @abstractmethod
    def transform1(self, source: T) -> V:
        pass

    @abstractmethod
    def transform2(self, source: T) -> X:
        pass
