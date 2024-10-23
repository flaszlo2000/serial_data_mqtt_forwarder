from abc import ABC, abstractmethod
from typing import Any, Callable, Final, Generic, Iterable, TypeVar, overload

from scheduling.scheduler_configuration import SchedulerConfiguration

T = TypeVar("T")
class Scheduler(ABC, Generic[T]):
    @overload
    @abstractmethod
    def schedule(self, data: Any, callback: Callable[[T], Any]) -> None:...
    @overload
    @abstractmethod
    def schedule(self, data: Any, callback: Callable[[T], Any], *, send_first_value: bool = True) -> None:...

    @abstractmethod
    def schedule(self, data: Any, callback: Callable[[T], Any], *, send_first_value: bool = True) -> None:
        ...

class ConfiguredScheduler(Scheduler[T]):
    """""" # TODO
    def __init__(self, configs: Iterable[SchedulerConfiguration]) -> None:
        super().__init__()

        self.configs: Final[Iterable[SchedulerConfiguration]] = configs
