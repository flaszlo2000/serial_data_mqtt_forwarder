from logging import Logger
from queue import Queue
from signal import SIGINT, signal
from threading import Event, Thread
from typing import Final, NoReturn, Optional

from app_util import AppUtil
from exc import DataForwarderConnectionException
from lib.configs import (Config, MqttConfig, SerialDeviceConfig,
                         SerialDeviceNotFoundException, get_config)
from lib.data_forwarding import DataForwarderBase, MqttDataInputDTO
from lib.logging_configurator import setup_logger
from lib.serial_handling import SerialDeviceHandler
from retry_decorator import retry_with_pow2_delay_policy


class App:
    "" # TODO this + comments
    def __init__(self, config: Config, stop_event: Event, logger: Logger) -> None:
        self._stop_event = stop_event
        self.logger = logger

        self.__mqtt_config: Final[MqttConfig] = config.getMqttConfig()
        self.__serial_device_config: Final[SerialDeviceConfig] = config.getSerialDeviceConfig()
        self.__message_queue: Queue[MqttDataInputDTO] = Queue(maxsize = config.msg_queue_size)

        self._serial_device_handler = SerialDeviceHandler[MqttDataInputDTO](
            self.__serial_device_config,
            self.__message_queue,
            MqttDataInputDTO.createFromString,
            logger
        )

        self.__app_util: Final[AppUtil] = AppUtil()

        self._data_forwarder: DataForwarderBase[MqttDataInputDTO] = self.__app_util.setup_data_forwarder(config, stop_event, logger)
        self.connect_data_forwarder()

        self._mqtt_handler_thread = Thread(
            target = self.__app_util.data_forwarder_thread,
            args = [self._data_forwarder, self.__message_queue, stop_event, logger]
        )

    @property
    def stopEvent(self) -> Event:
        return self._stop_event

    @retry_with_pow2_delay_policy(exc_occured = [DataForwarderConnectionException, OSError], retry_count = 3)
    def connect_data_forwarder(self) -> Optional[NoReturn]:
        "Tries to connect to the given data forwarder and properly logs the outcome"
        successful_connection = self._data_forwarder.connect()

        if not successful_connection:
            raise DataForwarderConnectionException(f"Couldn't connect to {self.__mqtt_config.host}")

        self.logger.info(f"Successfully connected to: {self.__mqtt_config.host}")

    @retry_with_pow2_delay_policy(exc_occured = [SerialDeviceNotFoundException], retry_count = 3)
    def checkData(self) -> Optional[NoReturn]:
        self.__serial_device_config.checkDevie()

    def start(self) -> None:
        signal(SIGINT, lambda _, __: self.__app_util.graceful_exit(self._stop_event, self._mqtt_handler_thread))

        self._mqtt_handler_thread.start()
        self._serial_device_handler.start(self._stop_event)

        self._mqtt_handler_thread.join()


def main() -> None:
    config: Final[Config] = get_config()
    logger: Final[Logger] = setup_logger(config.log_file_path)
    stop_event = Event()
    
    try:
        main_app = App(config, stop_event, logger)
        main_app.checkData()
    except Exception as exc: # pokemon!
        logger.exception(exc)
        stop_event.set()

        raise

if __name__ == "__main__":
    main()