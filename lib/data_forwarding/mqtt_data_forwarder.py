from dataclasses import dataclass
from json import JSONDecodeError
from json import loads as json_loads
from logging import Logger
from threading import Event
from typing import Any, Dict, Final, Optional, overload

from configs.mqtt_config import MqttConfig
from data_forwarding.data_forwarding_base import DataForwarderBase
from data_forwarding.exc import SendingUnsuccessfulException
from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion, MQTTErrorCode
from utils.policies import RetryPolicy
from utils.retry_policy import RetryWithPow2DelayPolicy


@dataclass
class MqttDataInputDTO: # NOTE: must comply to DataInputDTOProtocol
    destination: str
    data: str

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
    def __init__(self, mqtt_config: MqttConfig, stop_event: Event, logger: Logger) -> None:
        self.__mqtt_config: Final[MqttConfig] = mqtt_config
        self.stop_event = stop_event
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


    @overload
    def retySend(self, data_dto: MqttDataInputDTO) -> None:...
    @overload
    def retySend(self, data_dto: MqttDataInputDTO, retry_strategy: RetryPolicy) -> None:...
    
    def retySend(self, data_dto: MqttDataInputDTO, retry_strategy: Optional[RetryPolicy] = None) -> None:
        "Tries to resend the given data_dto with the given retry strategy (thats is optional and fallbacks to pow2 delayed strategy)"
        def sending_that_raises() -> bool:
            # Inner function that tries to send the data vut raises exception if it was unsuccessful
            result = self._mqtt_client.publish(data_dto.destination, data_dto.data)

            if not result.is_published():
                self.logger.warning(f"Message forwarding retry failed with: {result.rc}")
                raise SendingUnsuccessfulException()
            
            return result.is_published()

        retry_strategy = retry_strategy or RetryWithPow2DelayPolicy()

        result = retry_strategy.retry(
            sending_that_raises,
            self.stop_event,
            [SendingUnsuccessfulException],

            fail_message = "Wasn't able to forward the message, even after repeated jittered retrying."
        )

        assert result is not None
        self.logger.info("Retry policy successfully forwarded the message")
