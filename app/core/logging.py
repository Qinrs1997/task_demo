import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(
    level: str = "INFO",
    log_file: str = "logs/app.log",
    error_log_file: str = "logs/error.log",
    log_to_console: bool = False,
) -> None:
    log_level = getattr(logging, level.upper(), logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )

    handlers: list[logging.Handler] = []

    app_log_path = Path(log_file)
    app_log_path.parent.mkdir(parents=True, exist_ok=True)
    app_handler = RotatingFileHandler(
        app_log_path,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    app_handler.setLevel(log_level)
    app_handler.setFormatter(formatter)
    handlers.append(app_handler)

    error_log_path = Path(error_log_file)
    error_log_path.parent.mkdir(parents=True, exist_ok=True)
    error_handler = RotatingFileHandler(
        error_log_path,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    handlers.append(error_handler)

    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    root_logger.setLevel(log_level)
    for handler in handlers:
        root_logger.addHandler(handler)
