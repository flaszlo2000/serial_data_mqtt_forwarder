import logging
from pathlib import Path
from typing import Optional


def get_configured_logger(out_file_path: Path, logger_name: str = __name__) -> logging.Logger:
    "Creates and configures a new logger"
    if not out_file_path.exists():
        raise FileNotFoundError(f"{out_file_path.name} was not found to log into!")

    logger = logging.getLogger(logger_name)
    logging.basicConfig(
        filename = out_file_path,
        format = "%(asctime)s: %(levelname)s : %(message)s",
        datefmt = "%Y.%m.%d %H:%M:%S",
        level = logging.DEBUG
    )

    return logger

def setup_logger(out_file_path: Optional[Path] = None) -> logging.Logger:
    "Setups a logger with an output file"
    log_file_was_created: bool = False
    out_file_path = out_file_path or Path("./log.log")

    if not out_file_path.exists():
        out_file_path.touch()

        log_file_was_created = out_file_path.exists()
    
    logger = get_configured_logger(out_file_path)

    if log_file_was_created:
        logger.info("The log file was created automatically")

    return logger