from dataclasses import dataclass, field
from os import getenv
from typing import Callable

from dataclass_fallback_field import FallbackFieldMixin
from env_config_keys import EnvConfigKey


def getEnvValue(env_key: EnvConfigKey) -> Callable[[], str]:
    return lambda: getenv(env_key.value) or ""

@dataclass
class Config(FallbackFieldMixin):
    msg_queue_size: int = field(init = False)
    _msg_queue_size: str = field(default_factory = getEnvValue(EnvConfigKey.MSG_QUEUE_SIZE))
