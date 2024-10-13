from contextlib import contextmanager
from dataclasses import dataclass
from logging import Logger
from queue import Queue
from threading import Event
from typing import Callable, Generator, Generic, Optional

from serial import Serial

from configs import SerialDeviceConfig
from data_forwarding import T_DTO


@dataclass
class SerialDeviceHandler(Generic[T_DTO]):
    config: SerialDeviceConfig
    message_queue: "Queue[T_DTO]"
    message_converter_factory: Callable[[str, Logger], Optional[T_DTO]]
    logger: Logger

    @contextmanager
    def setupSerialDevice(self) -> Generator[Serial, None, None]:
        yield Serial(
            self.config.device_path.as_posix(),
            self.config.baud_rate
        )
    
    def start(self, stop_event: Event, *, polling_interval: float = 0.1) -> None:
        with self.setupSerialDevice() as serial_device:
            self.logger.info(f"Serial connection to {self.config.device_path} is established.")

            if serial_device.writable():
                # TODO: write config
                pass

            while not stop_event.wait(polling_interval):
                if serial_device.in_waiting == 0: continue

                data: str = serial_device.readline().decode().strip()
                message: Optional[T_DTO] = self.message_converter_factory(data, self.logger) 

                if message is None:
                    self.logger.error(f"{data} is incorrectly formatted, it won't be forwarded!")

                    continue

                self.message_queue.put(message)
