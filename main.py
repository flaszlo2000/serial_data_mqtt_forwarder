from logging import Logger
from queue import Queue
from signal import SIGINT, signal
from threading import Event, Thread
from typing import Any, Final, NoReturn, Optional

from dotenv import load_dotenv

from config import Config, MqttConfig
from data_forwarding import DataForwarderBase, DataInputDTOProtocol
from exc import DataForwarderConnectionException
from logging_config import setup_logger
from mqtt_data_forwarder import MqttDataForwarder, MqttDataInputDTO


def _graceful_exit(stop_event: Event, message_forwarder_thread: Thread) -> None:
    "Gracefully stops the program, designed to react to SIGINT"
    stop_event.set()
    message_forwarder_thread.join()

def data_forwarder_thread(
    data_forwarder: DataForwarderBase[Any],
    msg_queue: "Queue[DataInputDTOProtocol]",
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

            if not sent:
                logger.warning(f"Message ({message}) couldn't be sent, retrying")
                
                if message.retries < message.max_retries:
                    msg_queue.put(message) # TODO: use proper retry policy
                    message.increaseRetries()

                    continue
                
                if message.retries >= message.max_retries:
                    logger.error(f"Message ({message}) couldn't be sent, dropping")

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

    mqtt_handler_thread = Thread(
        target = data_forwarder_thread,
        args = [mqtt_data_forwarder, message_queue, stop_event, logger]
    )

    signal(SIGINT, lambda _, __: _graceful_exit(stop_event, mqtt_handler_thread))
    mqtt_handler_thread.start()

    mqtt_handler_thread.join()

if __name__ == "__main__":
    load_dotenv()

    config: Final[Config] = Config()
    logger: Final[Logger] = setup_logger(config.log_file_path)
    stop_event = Event()
    
    try:
        main(config, logger, stop_event)
    except Exception as exc: # pokemon!
        logger.exception(exc)
        stop_event.set()

        raise
