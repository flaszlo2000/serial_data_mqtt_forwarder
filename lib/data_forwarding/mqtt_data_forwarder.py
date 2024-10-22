from dataclasses import dataclass, field
from json import JSONDecodeError
from json import loads as json_loads
from logging import Logger
from typing import Any, Dict, Final, Optional

from configs.mqtt_config import MqttConfig
from data_forwarding.data_forwarding_base import DataForwarderBase
from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode


@dataclass
class MqttDataInputDTO: # NOTE: must comply to DataInputDTOProtocol
    destination: str
    data: str

    retries: int = field(default = 0, repr = False)
    max_retries: int = field(default = 3, repr = False)

    def increaseRetries(self, amount: int = 1) -> None:
        self.retries += amount

    @classmethod
    def createFromString(cls, _input: str, logger: Logger) -> "Optional[MqttDataInputDTO]":
        "Creates an instance based on _onput, the expected input is a json with the same fields as this class' required fields"
        result: Optional[MqttDataInputDTO] = None

        try:
            json: Dict[str, Any] = json_loads(_input)
            result = cls(**json)
        except (TypeError, JSONDecodeError) as exc:
            logger.exception(exc)

        return result

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
            if exc.errno == 101: # network is unreachable
                self.logger.error("Network is unreachable!")
      
                return False
            
            raise

        return connection_status is MQTTErrorCode.MQTT_ERR_SUCCESS

    def send(self, data_dto: MqttDataInputDTO) -> bool:
        result = self._mqtt_client.publish(data_dto.destination, data_dto.data)

        if not result.is_published():
            self.logger.error(result.rc)

        return result.is_published()

    def retySend(self, data_dto: MqttDataInputDTO) -> None:
        # TODO

        # if message.retries < message.max_retries:
        #     msg_queue.put(message) # TODO: use proper retry policy
        #     message.increaseRetries()

        #     continue
        
        # if message.retries >= message.max_retries:
        #     logger.error(f"Message ({message}) couldn't be sent, dropping")

        ...