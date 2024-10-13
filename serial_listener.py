from contextlib import contextmanager
from logging import Logger
from queue import Queue
from threading import Event
from typing import Generator, Generic

from serial import Serial

from configs import SerialDeviceConfig
from data_forwarding import T_DTO


class SerialDeviceHandler(Generic[T_DTO]):
    def __init__(self, config: SerialDeviceConfig, queue: "Queue[T_DTO]", logger: Logger) -> None:
        self.config = config
        self.msg_queue = queue
        self.logger = logger

    @contextmanager
    def setupSerialDevice(self) -> Generator[Serial, None, None]:
        yield Serial(
            self.config.device_path.as_posix(),
            self.config.baud_rate
        )
    
    def start(self, stop_event: Event, *, polling_interval: float = 0.1) -> None:
        with self.setupSerialDevice() as serial_device:
            self.logger.info(f"Serial connection to {self.config.device_path} is established.")

            # TODO: if writable then send config to it

            while not stop_event.wait(polling_interval):
                if serial_device.in_waiting == 0: continue

                data: str = serial_device.readline().decode().strip()
                # TODO: convert data to queue compatible format
                print(data)
