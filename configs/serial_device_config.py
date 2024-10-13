from dataclasses import dataclass
from pathlib import Path

from configs.esp_config import EspConfig
from exc import (IncompatibleSerialDeviceException,
                 SerialDeviceNotFoundException)


@dataclass
class SerialDeviceConfig:
    device_path: Path
    config: EspConfig
    baud_rate: int

    def __post_init__(self) -> None:
        if not self.device_path.exists():
            raise SerialDeviceNotFoundException(f"{self.device_path} does not exist!")
        
        if not self.device_path.is_char_device():
            raise IncompatibleSerialDeviceException(f"{self.device_path} is incompatible! We need a char device!")
