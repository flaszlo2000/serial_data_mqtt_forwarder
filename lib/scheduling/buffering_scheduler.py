from dataclasses import dataclass
from threading import Timer
from typing import Any, Callable, Dict, Final, Iterable, List, Optional, cast

from data_forwarding.data_forwarding_base import T_DTO
from exc import SchedulerConfigException
from scheduling import ConfiguredScheduler, TimedSchedulerConfiguration


@dataclass
class NamedTimer:
    name: str
    timer: Timer

class MqttBufferingScheduler(ConfiguredScheduler[T_DTO]):
    """""" # TODO
    def __init__(self, configs: Iterable[TimedSchedulerConfiguration], data_buffer: Optional[Dict[str, T_DTO]] = None) -> None:
        super().__init__(configs)

        # TODO: make this configurable from HA

        self.__topic_data_buffer: Dict[str, T_DTO] = data_buffer or dict()
        self.__named_timers: List[NamedTimer] = list()

    def getNamedTimer(self, topic: str) -> Optional[NamedTimer]:
        "Returns the named timer based on the given topic, if it was not found, returns None"
        result: Optional[NamedTimer] = None
        
        for named_timer in self.__named_timers:
            if named_timer.name == topic:
                result = named_timer
                break
        
        return result

    def __handleCallback(self, topic: str, callback: Callable[[T_DTO], Any]) -> None:
        "Removes the named_timer from the saved ones based on the given topic and calls callback"
        named_timer_for_topic = self.getNamedTimer(topic)
        
        if named_timer_for_topic is None:
            raise RuntimeError("__handleCallback was called but timer that should have called it was not found!")

        self.__named_timers.remove(named_timer_for_topic)
        data_to_send = self.__topic_data_buffer.pop(topic)

        callback(data_to_send)

    def _hasTimerForTopic(self, topic: str) -> bool:
        "Checks if the instance already has a timer for the given topic"
        return any(map(lambda named_timer: named_timer.name == topic, self.__named_timers))

    def _getConfigForTopic(self, topic: str) -> Optional[TimedSchedulerConfiguration]:
        "Returns the configuration to the given topic"
        result: Optional[TimedSchedulerConfiguration] = None
        
        for config in cast(Iterable[TimedSchedulerConfiguration], self.configs):
            if config.topic == topic:
                result = config
                break
        
        return result

    def _hasConfigForTopic(self, topic: str) -> bool:
        "Checks if the instance has config for the given topic"

        return self._getConfigForTopic(topic) is not None

    @staticmethod
    def minsToMillisecond(min: float) -> float:
        "Converts minutes to milliseconds"
        return min * 60 * 1000

    def __addTimerForTopic(self, topic: str, callback: Callable[[T_DTO], Any]) -> None:
        "Setups and adds a named timer to the named timers based on the given arguments"
        config_for_topic: Final[Optional[TimedSchedulerConfiguration]] = self._getConfigForTopic(topic)
        
        if config_for_topic is None:
            raise SchedulerConfigException(f"Missing configuration for {topic}")

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
        "Saves the given data into the data buffer based on the data's destination"
        # NOTE: the reason to move this to a separate function is that, this way this can be overridden without changing any other logic
        # for instance: saving the last state, collecting all datas that the sensor sent and send it in bulk, etc.

        self.__topic_data_buffer[data.destination] = data

    def schedule(self, data: T_DTO, callback: Callable[[T_DTO], Any], *, send_first_value: bool = True) -> None:
        "Schedules a callback with the given data"
        if not self._hasConfigForTopic(data.destination):
            raise SchedulerConfigException(f"Missing configuration for {data.destination}")

        self.__saveData(data)

        if not self._hasTimerForTopic(data.destination):
            if send_first_value:
                callback(data)

            self.__addTimerForTopic(data.destination, callback)
