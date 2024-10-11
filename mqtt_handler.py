from dataclasses import dataclass
from logging import Logger
from typing import Final

from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode

from config import MqttConfig
from data_forwarding import DataForwarderBase, DataInputDTO


@dataclass
class MqttDataInputDTO(DataInputDTO):
    topic: str
    data: str

class MqttDataForwarder(DataForwarderBase[MqttDataInputDTO]):
    def __init__(self, mqtt_config: MqttConfig, logger: Logger) -> None:
        self.__mqtt_config: Final[MqttConfig] = mqtt_config
        self.logger = logger

        self._mqtt_client = Client(CallbackAPIVersion.VERSION2)
        self._mqtt_client.username_pw_set(self.__mqtt_config.username, self.__mqtt_config.password)
   
    def connect(self) -> bool:
        "Connects to the mqtt server. Returns True if the connection was successful"

        try:
            connection_status = self._mqtt_client.connect(
                self.__mqtt_config.ip, self.__mqtt_config.port, self.__mqtt_config.keepalive
            )
        except OSError as exc:
            if exc.errno == 101: # netwoek is unreachable
                self.logger.error("Network is unreachable!")
                return False
            
            raise

        return connection_status is MQTTErrorCode.MQTT_ERR_SUCCESS

    def send(self, data_dto: MqttDataInputDTO) -> bool:
        result = self._mqtt_client.publish(data_dto.topic, data_dto.data)

        return result.is_published()

