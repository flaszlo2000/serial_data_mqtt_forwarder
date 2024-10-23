import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Final, Optional, overload


@dataclass
class NamedLoggingHandler:
    name: str = field(hash = True)
    handler: logging.Handler = field(repr = False, hash = True)

    def __hash__(self) -> int:
        return id(self) # memory adrress for hash, fnv for the weak, yolo 


@overload
def get_configured_logger(out_file_path: Path) -> logging.Logger:...
@overload
def get_configured_logger(out_file_path: Path, logger_name: str = __name__) -> logging.Logger:...

def get_configured_logger(out_file_path: Path, logger_name: str = __name__) -> logging.Logger:
    "Creates and configures a new logger"
    if not out_file_path.exists():
        raise FileNotFoundError(f"{out_file_path.name} was not found to log into!")

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    formatter: Final[logging.Formatter] = logging.Formatter("%(asctime)s: %(levelname)s : %(message)s", datefmt = "%Y.%m.%d %H:%M:%S")
    handlers: Final[Dict[NamedLoggingHandler, int]] = {
        NamedLoggingHandler("console_handler", logging.StreamHandler()): logging.DEBUG,
        NamedLoggingHandler("out_file_handler", logging.FileHandler(out_file_path)): logging.INFO
    }

    for handler_config, loglevel in handlers.items():
        handler_config.handler.set_name(handler_config.name)
        handler_config.handler.setLevel(loglevel)
        handler_config.handler.setFormatter(formatter)

        logger.addHandler(handler_config.handler)

    return logger


@overload
def setup_logger() -> logging.Logger:...
@overload
def setup_logger(out_file_path: Path) -> logging.Logger:...

def setup_logger(out_file_path: Optional[Path] = None) -> logging.Logger:
    "Setups a logger with an output file"
    log_file_was_created: bool = False
    out_file_path = out_file_path or Path("./log.log")

    if not out_file_path.exists():
        out_file_path.touch()

        log_file_was_created = out_file_path.exists()
        assert log_file_was_created
    
    logger = get_configured_logger(out_file_path)

    if log_file_was_created:
        logger.info("The log file was created automatically")

    return logger
