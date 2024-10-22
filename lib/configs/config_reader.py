from functools import lru_cache
from json import load as json_load
from pathlib import Path
from typing import Any, Dict, Optional

from configs import Config
from exc import IncorrectConfigurationException


def read_config(config_path: Path) -> Dict[str, Any]:
    "Tries to return the json based config from the given file"
    if not config_path.exists():
        raise FileNotFoundError(f"{config_path} does not exist!")

    with open(config_path, "r") as config_file:
        return json_load(config_file)

@lru_cache
def get_config(config_path: Optional[Path] = None) -> Config:
    "Reads and returns the config"
    config_path = config_path or Path("./config.json")
    raw_config = read_config(config_path)

    try:
        config = Config(**raw_config)
    except TypeError as exc:
        raise IncorrectConfigurationException(exc)
    
    return config
