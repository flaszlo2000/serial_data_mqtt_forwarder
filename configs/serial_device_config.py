from dataclasses import dataclass
from pathlib import Path


@dataclass
class SerialDeviceConfig:
    device_path: Path
    baud_rate: int