from json import load as json_load
from pathlib import Path
from typing import Dict, List

from typing_extensions import TypeAlias

EspConfig: TypeAlias = Dict[str, List[str]]

def get_esp_config(esp_config_path: Path) -> EspConfig:
    if not esp_config_path.exists():
        raise FileNotFoundError(f"{esp_config_path} does not exist!")

    with open(esp_config_path, "r") as esp_config_file:
        esp_config: EspConfig = json_load(esp_config_file)

        return esp_config

