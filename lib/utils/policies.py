from threading import Event
from typing import Callable, Container, Protocol, Type, TypeVar, overload

T = TypeVar("T")

class RetryPolicy(Protocol):
    @overload
    @staticmethod
    def retry(function: Callable[..., T], stop_event: Event, exc_occured: Container[Type[Exception]]) -> T:...
    @overload
    @staticmethod
    def retry(function: Callable[..., T], stop_event: Event, exc_occured: Container[Type[Exception]], *, retry_count: int = 5) -> T:...
    @overload
    @staticmethod
    def retry(function: Callable[..., T], stop_event: Event, exc_occured: Container[Type[Exception]], *, fail_message: str) -> T:...
    @overload
    @staticmethod
    def retry(function: Callable[..., T], stop_event: Event, exc_occured: Container[Type[Exception]], *, retry_count: int = 5, fail_message: str = "") -> T:...

    @staticmethod
    def retry(function: Callable[..., T], stop_event: Event, exc_occured: Container[Type[Exception]], *, retry_count: int = 5, fail_message: str = "") -> T:...
