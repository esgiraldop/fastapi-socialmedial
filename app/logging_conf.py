from logging.config import dictConfig
from app.config import DevConfig, config


def configure_logging() -> None:
    # Adding logger configuration, handlers and formatters
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M-%S",
                    "format": "%(name)s:%(lineno)d - %(message)s",
                },  # Format of the log records to be displayed to the console
                "file": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M-%S",
                    "format": "%(asctime)s.%(msecs)03dZ | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    # "class": "logging.StreamHandler",
                    "class": "rich.logging.RichHandler",  # Better formatter than above
                    "level": "DEBUG",  # No log is filtered out,
                    "formatter": "console",  # Mapping the formatter defined above
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "app.log",
                    "maxBytes": 1024 * 1024 * 5,  # 5MB until new file is created
                    "backupCount": 5,  # How many files will be kept
                    "encoding": "utf8",
                },  # Rotating means every time the file gets full, another file is created
            },
            "loggers": {
                "uvicorn": {
                    "handlers": [
                        # "default", # fastapi is enough
                        "rotating_file"
                    ],
                    "level": "INFO",
                },
                "app": {  # The logger from which all other handlers will inherit. "app" is the application folder
                    "handlers": [
                        "default",
                        "rotating_file",
                    ],  # Multiple handlers can be defined for console, for a file, etc
                    "level": "DEBUG"
                    if isinstance(config, DevConfig)
                    else "INFO",  # Depending on the mode defined in the .env file, I want to select to logging mode. "INFO" mode filters out some logs
                    "propagate": False,  # Doesn't send any logger created in "app", to it's parent, which is the root logger.
                },
                "databases": {"handlers": ["default"], "level": "WARNING"},
                "aiosqlite": {"handlers": ["default"], "level": "WARNING"},
            },
        }
    )
