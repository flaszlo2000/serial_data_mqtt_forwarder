from logging import Logger
from queue import Queue
from signal import SIGINT, signal
from threading import Event, Thread
from typing import Any, Final, NoReturn, Optional

from dotenv import load_dotenv

from config import Config, MqttConfig
from data_forwarding import DataForwarderBase, DataInputDTO
from exc import DataForwarderConnectionException
from loggin_handler import setup_logger
from mqtt_handler import MqttDataForwarder, MqttDataInputDTO


def data_forwarder_thread(data_forwarder: DataForwarderBase[DataInputDTO], msg_queue: "Queue[DataInputDTO]", stop_event: Event, *, polling_interval: float = 0.1) -> None:
    "Forwards data thru the data_forwarder on the given queue. This is designed to be run on a separate thread"
    # TODO: acquire logger in a thread safe way

    while not stop_event.wait(polling_interval):
        if msg_queue.empty(): continue
        
        while not msg_queue.empty():
            sent = data_forwarder.send(msg_queue.get_nowait())

            if not sent:
                #! TODO: logging + retry
                pass

def _graceful_exit(stop_event: Event) -> None:
    stop_event.set()
    # TODO: join thread?

def connect_data_forwarder(data_forwarder: DataForwarderBase[Any], logger: Logger, host: str) -> Optional[NoReturn]:
    "Tries to connect to the given data forwarder and properly logs the outcome"
    successful_connection = data_forwarder.connect()

    if not successful_connection:
        raise DataForwarderConnectionException(f"Couldn't connect to {host}")

    logger.info(f"Successfully connected to: {host}")

def main(config: Config, logger: Logger, stop_event: Event) -> None:
    mqtt_config: Final[MqttConfig] = config.getMqttConfig()
    message_queue: Queue[MqttDataInputDTO] = Queue(maxsize = config.msg_queue_size)
    
    mqtt_data_forwarder = MqttDataForwarder(mqtt_config, logger)
    connect_data_forwarder(mqtt_data_forwarder, logger, mqtt_config.host)

    mqtt_handler_thread = Thread(target = data_forwarder_thread, args = [mqtt_data_forwarder, message_queue, stop_event])

    signal(SIGINT, lambda _, __: _graceful_exit(stop_event))
    mqtt_handler_thread.start()

if __name__ == "__main__":
    load_dotenv()

    config: Final[Config] = Config()
    logger: Final[Logger] = setup_logger(config.log_file_path)
    stop_event = Event()
    
    try:
        main(config, logger, stop_event)
    except Exception as exc: # pokemon!
        logger.error(exc)
        stop_event.set()

        raise
