from abc import ABC
from dataclasses import dataclass


class SchedulerConfiguration(ABC):
    ...


@dataclass
class TimedSchedulerConfiguration(SchedulerConfiguration):
    topic: str
    time_in_minutes: float