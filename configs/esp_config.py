from json import load as json_load
from pathlib import Path
from typing import Dict, List

from typing_extensions import TypeAlias

EspConfig: TypeAlias = Dict[str, List[str]]

def get_esp_config(esp_config_path: Path) -> EspConfig:
    "Tries to return the esp's config from the given file"
    if not esp_config_path.exists():
        raise FileNotFoundError(f"{esp_config_path} does not exist!")

    with open(esp_config_path, "r") as esp_config_file:
        dirty_esp_config: EspConfig = json_load(esp_config_file)

        # NOTE: upper mac's are needed because the data that the esp receives is in uppercase too
        return {mac.upper() : access_list for mac, access_list in dirty_esp_config.items()}
