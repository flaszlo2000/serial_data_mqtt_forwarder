from dataclasses import dataclass, field


@dataclass
class Config:
    msg_queue_size: int = field(default = 100)