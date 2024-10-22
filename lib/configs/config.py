from dataclasses import dataclass, field
from pathlib import Path
from typing import Collection, Iterable, List, NoReturn, Optional

from configs.aliases import EspConfig, TimedSchedulerConfigs
from configs.exc import (IncorrectConfigurationException,
                         MissingConfigurationException)
from configs.mqtt_config import MqttConfig
from configs.serial_device_config import SerialDeviceConfig
from scheduling.scheduler_configuration import TimedSchedulerConfiguration
from utils.dataclass_fallback_field import FallbackFieldMixin


@dataclass
class Config(FallbackFieldMixin):
    log_file_path: Path = field(init = False)
    _log_file_path: str = field(repr = False)

    msg_queue_size: int

    mqtt_username: str
    mqtt_password: str
    mqtt_ip: str
    mqtt_port: int
    mqtt_keepalive: int

    serial_device_path: Path = field(init = False)
    _serial_device_path: str = field(repr = False)
    serial_device_baud_rate: int

    esp_config: EspConfig

    use_direct_forwarding: Optional[bool] = field(default = True)
    timed_scheduler_configs: Optional[TimedSchedulerConfigs] = field(default = None, repr = False)

    supress_logging_info: Optional[bool] = field(default = False) # TODO: use

    def _getParametersWithMissingValue(self, fields: Iterable[str]) -> Collection[str]:
        return list(filter(lambda key: getattr(self, key) == "", fields))

    def __dataCheck(self) -> Optional[NoReturn]:
        public_fields = filter(lambda key: not key.startswith("_"), self.__dict__) # this class uses FallbackFieldMixin so we only care about the public fields
        parameters_with_missing_value = self._getParametersWithMissingValue(public_fields)

        if len(parameters_with_missing_value) > 0:
            raise MissingConfigurationException(f"{parameters_with_missing_value=}")

        if self.use_direct_forwarding and self.timed_scheduler_configs is None:
            raise MissingConfigurationException("Without direct forwarding, timed scheduler configs are required!")

    def __correctData(self) -> None:
        # NOTE: upper mac's are needed because the data that the esp receives is in uppercase too
        self.esp_config = {mac.upper() : access_list for mac, access_list in self.esp_config.items()}

    def __post_init__(self) -> None:
        super().__post_init__()

        self.__dataCheck()
        self.__correctData()

    def getMqttConfig(self) -> MqttConfig:
        return MqttConfig(self.mqtt_username, self.mqtt_password, self.mqtt_ip, self.mqtt_port, self.mqtt_keepalive)

    def getSerialDeviceConfig(self) -> SerialDeviceConfig:
        return SerialDeviceConfig(
            self.serial_device_path,
            self.esp_config,
            self.serial_device_baud_rate
        )

    def getTimedSchedulerConfigs(self) -> List[TimedSchedulerConfiguration]:
        if self.use_direct_forwarding:
            raise IncorrectConfigurationException("With direct forwarding, timed scheduler configs are not available!")
        
        if self.timed_scheduler_configs is None:
            raise MissingConfigurationException("Missing timed scheduler configs")

        return list(
            map(
                lambda config: TimedSchedulerConfiguration(**config),
                self.timed_scheduler_configs
            )
        )
