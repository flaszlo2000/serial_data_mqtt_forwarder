from dataclasses import dataclass

from data_forwarding import DataForwarderBase


@dataclass
class MqttDataInputDTO:
    topic: str
    data: str

class MqttDataForwarder(DataForwarderBase):
    def __init__(self) -> None:
        ...

    def send(self, data: MqttDataInputDTO) -> bool:
        ...

