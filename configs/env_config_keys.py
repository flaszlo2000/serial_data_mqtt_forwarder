from enum import Enum
from os import getenv
from typing import Callable


class EnvConfigKey(str, Enum):
    LOG_FILE_PATH = "log_file_path"

    MSG_QUEUE_SIZE = "msg_queue_size"

    MQTT_USERNAME = "mqtt_username"
    MQTT_PASSWORD = "mqtt_password"
    MQTT_IP = "mqtt_ip"
    MQTT_PORT = "mqtt_port"
    MQTT_KEEPALIVE = "mqtt_keepalive"

    SERIAL_DEVICE_CONFIG_PATH = "serial_device_config_path"
    SERIAL_DEVICE_PATH = "serial_device_path"
    SERIAL_DEVICE_BAUD_RATE = "serial_device_baud_rate"

def get_env_value(env_key: EnvConfigKey) -> Callable[[], str]:
    """
    Tries to get the given env config key, it it does not exist then it gives back an empty string.
    It's designed to use with dataclass field's default_factory to make those a bit nicer
    """

    return lambda: getenv(env_key.value) or ""
