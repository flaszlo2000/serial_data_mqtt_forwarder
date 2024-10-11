from dataclasses import dataclass

from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion

from config import MqttConfig
from data_forwarding import DataForwarderBase, DataInputDTO


@dataclass
class MqttDataInputDTO(DataInputDTO):
    topic: str
    data: str

class MqttDataForwarder(DataForwarderBase[MqttDataInputDTO]):
    def __init__(self, mqtt_config: MqttConfig) -> None:
        self.mqtt_client = Client(CallbackAPIVersion.VERSION2)

        self.mqtt_client.username_pw_set(mqtt_config.username, mqtt_config.password)
        self.mqtt_client.connect(mqtt_config.ip, mqtt_config.port, mqtt_config.keepalive)

    def send(self, data_dto: MqttDataInputDTO) -> bool:
        result = self.mqtt_client.publish(data_dto.topic, data_dto.data)

        return result.is_published()

