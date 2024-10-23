from abc import ABC, abstractmethod
from typing import Generic, Optional, Protocol, TypeVar, overload

from utils.policies import RetryPolicy


class DataInputDTOProtocol(Protocol):
    destination: str


T_DTO = TypeVar("T_DTO", bound = DataInputDTOProtocol)
class DataForwarderBase(Generic[T_DTO], ABC):
    @abstractmethod
    def connect(self) -> bool:
        ...

    @abstractmethod
    def send(self, data_dto: T_DTO) -> bool:
        ...


    @overload
    @abstractmethod
    def retySend(self, data_dto: T_DTO) -> None:...
    @overload
    @abstractmethod
    def retySend(self, data_dto: T_DTO, retry_strategy: RetryPolicy) -> None:...

    @abstractmethod
    def retySend(self, data_dto: T_DTO, retry_strategy: Optional[RetryPolicy] = None) -> None:...
