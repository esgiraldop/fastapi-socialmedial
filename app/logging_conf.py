import logging

from logging.config import dictConfig

from app.config import DevConfig, config


def obfuscated(email: str, obfuscated_length: int) -> str:
    # with obfuscated_length = 2 :
    #   jhon.doe@example.com --> jh******@example.com
    characters = email[:obfuscated_length]
    first, last = email.split("@")
    return characters + ("*" * (len(first) - obfuscated_length)) + "@" + last


class EmailObfuscationFilter(logging.Filter):
    """Filter to hide some email information in the logs"""

    def __init__(self, name: str = "", obfuscated_length: int = 2) -> None:
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True


def configure_logging() -> None:
    # Adding logger configuration, handlers and formatters
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {  # Adds another variable to the formaters, so the id of the user making the request is printed at the beggining of the log
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    # Any parameter passed after "()", will be passed as keyword arguments to "asgi_correlation_id.CorrelationIdFilter"
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-",
                    # The three keywords above are equivalent to do "asgi_correlation_id.CorrelationIdFilter(uuid_length=8, default_value="-")"
                },
                "email_obfuscation": {
                    "()": EmailObfuscationFilter,  # If this was passed as a string (as for "asgi_correlation_id.CorrelationIdFilter" above), python would try to import it and use it, but we are just passing a class defined here
                    "obfuscated_length": 2 if isinstance(config, DevConfig) else 0,
                    # "name": "", # This is not needed since it is passed automatically
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M-%S",
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s",
                    # "format": "%(name)s:%(lineno)d - %(message)s",
                },  # Format of the log records to be displayed to the console
                "file": {
                    # "class": "logging.Formatter",  # For logging plain text
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",  # For loggin in json format, which is more useful when handing in the logs to another app
                    "datefmt": "%Y-%m-%dT%H:%M-%S",
                    "format": "%(asctime)s.%(msecs)03dZ | %(levelname)-8s | [%(correlation_id)s] %(name)s:%(lineno)d - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    # "class": "logging.StreamHandler",
                    "class": "rich.logging.RichHandler",  # Better formatter than above
                    "level": "DEBUG",  # No log is filtered out,
                    "formatter": "console",  # Mapping the formatter defined above
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "app.log",
                    "maxBytes": 1024 * 1024 * 5,  # 5MB until new file is created
                    "backupCount": 5,  # How many files will be kept
                    "encoding": "utf8",
                    "filters": ["correlation_id", "email_obfuscation"],
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
