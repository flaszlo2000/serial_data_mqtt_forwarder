from contextlib import contextmanager
from dataclasses import dataclass
from logging import Logger
from queue import Queue
from threading import Event
from typing import Callable, Final, Generator, Generic, Optional

from configs.serial_device_config import SerialDeviceConfig
from data_forwarding.data_forwarding_base import T_DTO
from serial import Serial


@dataclass
class SerialDeviceHandler(Generic[T_DTO]):
    device_config: SerialDeviceConfig
    message_queue: "Queue[T_DTO]"
    message_converter_factory: Callable[[str, Logger], Optional[T_DTO]]
    logger: Logger

    @contextmanager
    def setupSerialDevice(self) -> Generator[Serial, None, None]:
        yield Serial(
            self.device_config.device_path.as_posix(),
            self.device_config.baud_rate
        )
    
    def start(self, stop_event: Event, *, polling_interval: float = 0.1) -> None:
        with self.setupSerialDevice() as serial_device:
            self.logger.info(f"Serial connection to {self.device_config.device_path} is established.")

            # send config to the device
            #! ending \n is extremely important because we assume that the serial device uses 
            #! Serial.readStringUntil('\n') with a high reading timeout.
            #! With this setting, after it gets it's config, the reading will be instantly cancelled and
            #! the main program will start in the device.
            config_str: Final[str] = "".join((str(self.device_config.config), "\n"))
            serial_device.write(config_str.encode())
            
            self.logger.info(f"Device configuration has been sent to the device!")

            while not stop_event.wait(polling_interval):
                if serial_device.in_waiting == 0: continue

                data: str = serial_device.readline().decode().strip()
                message: Optional[T_DTO] = self.message_converter_factory(data, self.logger) 

                if message is None:
                    self.logger.error(f"*{data}* is incorrectly formatted, it won't be forwarded!")

                    continue

                self.message_queue.put(message)
