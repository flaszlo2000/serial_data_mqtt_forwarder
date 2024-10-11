from abc import ABC, abstractmethod
from typing import Generic, TypeVar


class DataInputDTO:
    ...

T_DTO = TypeVar("T_DTO", bound = DataInputDTO)
class DataForwarderBase(Generic[T_DTO], ABC):
    @abstractmethod
    def connect(self) -> bool:
        ...

    @abstractmethod
    def send(self, data_dto: T_DTO) -> bool:
        ...
