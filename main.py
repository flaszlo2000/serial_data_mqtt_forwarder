from logging import Logger
from queue import Queue
from signal import SIGINT, signal
from threading import Event, Thread
from typing import Any, Final, NoReturn, Optional

from lib.configs import Config, MqttConfig, SerialDeviceConfig, get_config
from lib.data_forwarding import (T_DTO, DataForwarderBase, MqttDataForwarder,
                                 MqttDataInputDTO,
                                 SchedulableDataForwarderProxy)
from lib.exc import DataForwarderConnectionException
from lib.logging_configurator import setup_logger
from lib.scheduling.buffering_scheduler import MqttBufferingScheduler
from lib.serial_listener import SerialDeviceHandler


def _graceful_exit(stop_event: Event, message_forwarder_thread: Thread) -> None:
    "Gracefully stops the program, designed to react to SIGINT"
    stop_event.set()
    message_forwarder_thread.join()

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

def connect_data_forwarder(data_forwarder: DataForwarderBase[Any], logger: Logger, host: str) -> Optional[NoReturn]:
    "Tries to connect to the given data forwarder and properly logs the outcome"
    successful_connection = data_forwarder.connect()

    if not successful_connection:
        raise DataForwarderConnectionException(f"Couldn't connect to {host}")

    logger.info(f"Successfully connected to: {host}")

def setup_data_forwarder(config: Config, logger: Logger) -> DataForwarderBase[Any]:
    mqtt_config: Final[MqttConfig] = config.getMqttConfig()
    mqtt_data_forwarder = MqttDataForwarder(mqtt_config, logger) 
   
    if config.use_direct_forwarding:
        return mqtt_data_forwarder
 

    configured_scheduler = MqttBufferingScheduler[MqttDataInputDTO](config.getTimedSchedulerConfigs())
        
    return SchedulableDataForwarderProxy[MqttDataInputDTO](
        mqtt_data_forwarder,
        configured_scheduler,
        logger
    )

def main(config: Config, logger: Logger, stop_event: Event) -> None:
    mqtt_config: Final[MqttConfig] = config.getMqttConfig()
    serial_device_config: Final[SerialDeviceConfig] = config.getSerialDeviceConfig()
    message_queue: Queue[MqttDataInputDTO] = Queue(maxsize = config.msg_queue_size)

    serial_device_handler = SerialDeviceHandler[MqttDataInputDTO](
        serial_device_config,
        message_queue,
        MqttDataInputDTO.createFromString,
        logger
    )

    data_forwarder: DataForwarderBase[MqttDataInputDTO] = setup_data_forwarder(config, logger)
    connect_data_forwarder(
        data_forwarder,
        logger,
        mqtt_config.host
    )

    mqtt_handler_thread = Thread(
        target = data_forwarder_thread,
        args = [data_forwarder, message_queue, stop_event, logger]
    )

    signal(SIGINT, lambda _, __: _graceful_exit(stop_event, mqtt_handler_thread))
    mqtt_handler_thread.start()
    serial_device_handler.start(stop_event)

    mqtt_handler_thread.join()

if __name__ == "__main__":
    config: Final[Config] = get_config()
    logger: Final[Logger] = setup_logger(config.log_file_path)
    stop_event = Event()
    
    try:
        main(config, logger, stop_event)
    except Exception as exc: # pokemon!
        logger.exception(exc)
        stop_event.set()

        raise
