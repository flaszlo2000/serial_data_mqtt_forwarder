from abc import ABC, abstractmethod
from typing import Generic, Protocol, TypeVar


class DataInputDTOProtocol(Protocol):
    destination: str

    retries: int
    max_retries: int

    def increaseRetries(self, amount: int = 1) -> None:
        ...

T_DTO = TypeVar("T_DTO", bound = DataInputDTOProtocol)
class DataForwarderBase(Generic[T_DTO], ABC):
    @abstractmethod
    def connect(self) -> bool:
        ...

    @abstractmethod
    def send(self, data_dto: T_DTO) -> bool:
        ...

    @abstractmethod
    def retySend(self, data_dto: T_DTO) -> None:
        "Uses proper retry policy to try and send the data"
        ...