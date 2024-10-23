from logging import Logger
from queue import Queue
from threading import Event, Thread
from typing import Any, Final, overload

from lib.configs import Config, MqttConfig
from lib.data_forwarding import (T_DTO, DataForwarderBase, MqttDataForwarder,
                                 MqttDataInputDTO)
from lib.proxy import SchedulableDataForwarderProxy
from lib.scheduling import MqttBufferingScheduler


class AppUtil:
    "" # TODO this + comments
    @staticmethod
    def setup_data_forwarder(config: Config, stop_event: Event, logger: Logger) -> DataForwarderBase[Any]:
        mqtt_config: Final[MqttConfig] = config.getMqttConfig()
        mqtt_data_forwarder = MqttDataForwarder(mqtt_config, stop_event, logger) 
    
        if config.use_direct_forwarding:
            return mqtt_data_forwarder
    

        configured_scheduler = MqttBufferingScheduler[MqttDataInputDTO](config.getTimedSchedulerConfigs())
            
        return SchedulableDataForwarderProxy[MqttDataInputDTO](
            mqtt_data_forwarder,
            configured_scheduler,
            logger
        )

    @overload
    @staticmethod
    def data_forwarder_thread(
        data_forwarder: DataForwarderBase[T_DTO],
        msg_queue: "Queue[T_DTO]",
        stop_event: Event,
        logger: Logger,
    ) -> None:...
    @overload
    @staticmethod
    def data_forwarder_thread(
        data_forwarder: DataForwarderBase[T_DTO],
        msg_queue: "Queue[T_DTO]",
        stop_event: Event,
        logger: Logger,
        *,
        polling_interval: float = 0.1
    ) -> None:...

    @staticmethod
    def data_forwarder_thread(
        data_forwarder: DataForwarderBase[T_DTO],
        msg_queue: "Queue[T_DTO]",
        stop_event: Event,
        logger: Logger,
        *,
        polling_interval: float = 0.1
    ) -> None:
        "Forwards data thru the data_forwarder on the given queue. This is designed to be run on a separate thread"

        while not stop_event.wait(polling_interval):
            if msg_queue.empty(): continue
            
            while not msg_queue.empty():
                message = msg_queue.get_nowait()
                sent = data_forwarder.send(message)

                if sent:
                    logger.info(f"Message forwarded successfully to {message.destination}!")
                else:
                    logger.warning(f"Message ({message}) couldn't be sent, retrying")

                    data_forwarder.retySend(message)

    @staticmethod
    def graceful_exit(stop_event: Event, message_forwarder_thread: Thread) -> None:
        "Gracefully stops the program, designed to react to SIGINT"
        stop_event.set()
        message_forwarder_thread.join()
        # TODO: stop timers