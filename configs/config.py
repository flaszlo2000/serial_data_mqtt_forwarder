from dataclasses import dataclass, field
from pathlib import Path
from typing import Collection, Iterable

from configs.mqtt_config import MqttConfig
from configs.serial_device_config import SerialDeviceConfig
from dataclass_fallback_field import FallbackFieldMixin
from env_config_keys import EnvConfigKey, get_env_value
from exc import MissingConfigurationException


@dataclass
class Config(FallbackFieldMixin):
    # TODO: optional config?
    
    log_file_path: Path = field(init = False)
    _log_file_path: str = field(default_factory = get_env_value(EnvConfigKey.LOG_FILE_PATH), repr = False)

    msg_queue_size: int = field(init = False)
    _msg_queue_size: str = field(default_factory = get_env_value(EnvConfigKey.MSG_QUEUE_SIZE), repr = False)

    mqtt_username: str = field(default_factory = get_env_value(EnvConfigKey.MQTT_USERNAME))
    mqtt_password: str = field(default_factory = get_env_value(EnvConfigKey.MQTT_PASSWORD), repr = False)
    mqtt_ip: str = field(default_factory = get_env_value(EnvConfigKey.MQTT_IP))
    mqtt_port: int = field(init = False)
    _mqtt_port: str = field(default_factory = get_env_value(EnvConfigKey.MQTT_PORT), repr = False)
    mqtt_keepalive: int = field(init = False)
    _mqtt_keepalive: str = field(default_factory = get_env_value(EnvConfigKey.MQTT_KEEPALIVE), repr = False)

    serial_device_path: Path = field(init = False)
    _serial_device_path: str = field(default_factory = get_env_value(EnvConfigKey.SERIAL_DEVICE_PATH), repr = False)
    serial_device_baud_rate: int = field(init = False)
    _serial_device_baud_rate: str = field(default_factory = get_env_value(EnvConfigKey.SERIAL_DEVICE_BAUD_RATE), repr = False)
    
    def _getParametersWithMissingValue(self, fields: Iterable[str]) -> Collection[str]:
        return list(filter(lambda key: getattr(self, key) == "", fields))

    def __post_init__(self) -> None:
        super().__post_init__()

        public_fields = filter(lambda key: not key.startswith("_"), self.__dict__) # this class uses FallbackFieldMixin so we only care about the public fields
        parameters_with_missing_value = self._getParametersWithMissingValue(public_fields)

        if len(parameters_with_missing_value) > 0:
            raise MissingConfigurationException(f"{parameters_with_missing_value=}")

    def getMqttConfig(self) -> MqttConfig:
        return MqttConfig(self.mqtt_username, self.mqtt_password, self.mqtt_ip, self.mqtt_port, self.mqtt_keepalive)

    def serialDeviceConfig(self) -> SerialDeviceConfig:
        return SerialDeviceConfig(self.serial_device_path, self.serial_device_baud_rate)