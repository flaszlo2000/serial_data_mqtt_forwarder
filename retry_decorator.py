from functools import wraps
from threading import Event
from typing import (Callable, Container, Optional, Protocol, Type, TypeVar,
                    cast, overload)

from typing_extensions import ParamSpec

from lib.utils.retry_policy import RetryWithPow2DelayPolicy


class HasStopEvent(Protocol):
    @property
    def stopEvent(self) -> Event:
        ...

T = TypeVar("T")
P = ParamSpec("P")


@overload
def retry_with_pow2_delay_policy(*, exc_occured: Container[Type[Exception]]) -> Callable[[Callable[..., T]], Callable[..., T]]:...
@overload
def retry_with_pow2_delay_policy(*, exc_occured: Container[Type[Exception]], retry_count: int = 5) -> Callable[[Callable[..., T]], Callable[..., T]]:...
@overload
def retry_with_pow2_delay_policy(*, exc_occured: Container[Type[Exception]], fail_message: str) -> Callable[[Callable[..., T]], Callable[..., T]]:...
@overload
def retry_with_pow2_delay_policy(*, exc_occured: Container[Type[Exception]], retry_count: int = 5, fail_message: Optional[str] = None) -> Callable[[Callable[..., T]], Callable[..., T]]:...

def retry_with_pow2_delay_policy(
    *,
    exc_occured: Container[Type[Exception]],
    retry_count: int = 5,
    fail_message: Optional[str] = None
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    "" # TODO
    def wrapper(function: Callable[P, T]) -> Callable   [P, T]:
        @wraps(function)
        def inner(*args: P.args, **kwargs: P.kwargs) -> T:
            return RetryWithPow2DelayPolicy.retry(
                lambda: function(*args, **kwargs),
                cast(HasStopEvent, args[0]).stopEvent,
                exc_occured,

                retry_count = retry_count,
                fail_message = fail_message
            )

        return inner
    return wrapper