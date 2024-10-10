from abc import ABC, abstractmethod
from typing import Any


class DataForwarderBase(ABC):
    @abstractmethod
    def send(self, data: Any) -> bool:
        ...
