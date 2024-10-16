from dataclasses import dataclass
from threading import Timer
from typing import Any, Callable, Dict, Final, Iterable, List, Optional

from data_forwarding.data_forwarding import T_DTO
from data_forwarding.scheduling import (ConfiguredScheduler,
                                        TimedSchedulerConfiguration)
from exc import SchedulerConfigException


@dataclass
class NamedTimer:
    name: str
    timer: Timer

class MqttBufferingScheduler(ConfiguredScheduler[T_DTO]):
    """""" # TODO
    def __init__(self, configs: Iterable[TimedSchedulerConfiguration], data_buffer: Optional[Dict[str, T_DTO]] = None) -> None:
        super().__init__(configs)

        # TODO: make this configurable from HA
        # TODO: docstrings

        self.__topic_data_buffer: Dict[str, T_DTO] = data_buffer or dict()
        self.__named_timers: List[NamedTimer] = list()

    def getNamedTimer(self, topic: str) -> Optional[NamedTimer]:
        result: Optional[NamedTimer] = None
        
        for named_timer in self.__named_timers:
            if named_timer.name == topic:
                result = named_timer
                break
        
        return result

    def __handleCallback(self, topic: str, callback: Callable[[T_DTO], Any]) -> None:
        named_timer_for_topic = self.getNamedTimer(topic)
        
        if named_timer_for_topic is None:
            raise RuntimeError("__handleCallback was called but timer that should have called it was not found!")

        self.__named_timers.remove(named_timer_for_topic)
        data_to_send = self.__topic_data_buffer.pop(topic)

        callback(data_to_send)

    def _hasTimerForTopic(self, topic: str) -> bool:
        return any(map(lambda named_timer: named_timer.name == topic, self.__named_timers))

    def _getConfigForTopic(self, topic: str) -> TimedSchedulerConfiguration:
        ... # TODO

    def _hasConfigForTopic(self, topic: str) -> bool:
        ... # TODO

    @staticmethod
    def minsToMillisecond(min: float) -> float:
        return min * 60 * 1000

    def __addTimerForTopic(self, topic: str, callback: Callable[[T_DTO], Any]) -> None:
        config_for_topic: Final[TimedSchedulerConfiguration] = self._getConfigForTopic(topic)
        
        named_timer = NamedTimer(
            name = topic,
            timer = Timer(
                self.minsToMillisecond(config_for_topic.time_in_minutes),
                self.__handleCallback,
                [topic, callback]
            )
        )

        named_timer.timer.start()
        self.__named_timers.append(named_timer)

    def __saveData(self, data: T_DTO) -> None:
        # NOTE: the reason to move this to a separate function is that, this way this can be overridden without changing any other logic
        # for instance: saving the last state, collecting all datas that the sensor sent and send it in bulk, etc.

        self.__topic_data_buffer[data.destination] = data

    def schedule(self, data: T_DTO, callback: Callable[[T_DTO], Any], *, send_first_value: bool = True) -> None:
        if not self._hasConfigForTopic(data.destination):
            raise SchedulerConfigException(f"Missing configuration for {data.destination}")

        self.__saveData(data)

        if not self._hasTimerForTopic(data.destination):
            if send_first_value:
                callback(data)

            self.__addTimerForTopic(data.destination, callback)
