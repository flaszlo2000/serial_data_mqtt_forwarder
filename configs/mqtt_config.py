from dataclasses import dataclass, field


@dataclass
class MqttConfig:
    username: str
    password: str = field(repr = False)

    ip: str
    port: int
    keepalive: int

    @property
    def host(self) -> str:
        return f"mqtt://{self.ip}:{self.port}"