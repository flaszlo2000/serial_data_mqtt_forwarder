from random import random
from threading import Event
from typing import Callable, Container, Optional, Type, TypeVar, overload

from utils.exc import RetryFail

T = TypeVar("T")

class RetryWithPow2DelayPolicy:
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
    def retry(function: Callable[..., T], stop_event: Event, exc_occured: Container[Type[Exception]], *, retry_count: int = 5, fail_message: Optional[str] = None) -> T:...

    @staticmethod
    def retry(
        function: Callable[..., T],
        stop_event: Event,
        exc_occured: Container[Type[Exception]],
        *,
        retry_count: int = 5, fail_message: Optional[str] = None
    ) -> T:
        "" # TODO this + comments
        result: Optional[T] = None
        exc_msg: Optional[str] = None

        for retry_i in range(retry_count):
            try:
                return function()
            except Exception as exc:
                if type(exc) not in exc_occured: raise
                
                jitted_time = 2 ** retry_i + random()
                print(f"{jitted_time=}")
                
                if (retry_i + 1) == retry_count:
                    exc_msg = str(exc)
                    continue

                stop_event.wait(jitted_time)
                continue
        
        if result is None:
            raise RetryFail(fail_message or exc_msg)

        return result
