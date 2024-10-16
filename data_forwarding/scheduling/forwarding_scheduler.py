from abc import ABC

from data_forwarding.scheduling.scheduler_configuration import \
    SchedulerConfiguration


class Scheduler(ABC):
    ...

class ConfiguredScheduler(Scheduler):
    def __init__(self, config: SchedulerConfiguration) -> None:
        super().__init__()

        self.config = config
