from dataclasses import dataclass, field
from os import getenv
from typing import Callable, Collection, Iterable

from dataclass_fallback_field import FallbackFieldMixin
from env_config_keys import EnvConfigKey
from exc import MissingConfigurationException


def getEnvValue(env_key: EnvConfigKey) -> Callable[[], str]:
    return lambda: getenv(env_key.value) or ""

@dataclass
class MqttConfig:
    username: str
    password: str = field(repr = False)

    ip: str
    port: int
    keepalive: int


@dataclass
class Config(FallbackFieldMixin):
    msg_queue_size: int = field(init = False)
    _msg_queue_size: str = field(default_factory = getEnvValue(EnvConfigKey.MSG_QUEUE_SIZE))

    mqtt_username: str = field(default_factory = getEnvValue(EnvConfigKey.MQTT_USERNAME))
    mqtt_password: str = field(default_factory = getEnvValue(EnvConfigKey.MQTT_PASSWORD), repr = False)
    mqtt_ip: str = field(default_factory = getEnvValue(EnvConfigKey.MQTT_IP))
    mqtt_port: int = field(init = False)
    _mqtt_port: str = field(default_factory = getEnvValue(EnvConfigKey.MQTT_PORT))
    mqtt_keepalive: int = field(init = False)
    _mqtt_keepalive: str = field(default_factory = getEnvValue(EnvConfigKey.MQTT_KEEPALIVE))

    
    def getParametersWithMissingValue(self, fields: Iterable[str]) -> Collection[str]:
        return list(filter(lambda key: getattr(self, key) == "", fields))

    def __post_init__(self) -> None:
        super().__post_init__()

        public_fields = filter(lambda key: not key.startswith("_"), self.__dict__)
        parameters_with_missing_value = self.getParametersWithMissingValue(public_fields)

        if len(parameters_with_missing_value) > 0:
            raise MissingConfigurationException(f"{parameters_with_missing_value=}")

    def getMqttConfig(self) -> MqttConfig:
        return MqttConfig(self.mqtt_username, self.mqtt_password, self.mqtt_ip, self.mqtt_port, self.mqtt_keepalive)
