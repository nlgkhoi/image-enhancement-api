import logging
import os
from logging.config import dictConfig

# # for sending error logs to slack
# import json
# import requests
# class HTTPSlackHandler(logging.Handler):
#     def emit(self, record):
#         log_entry = self.format(record)
#         json_text = json.dumps({"text": log_entry})
#         url = 'https://hooks.slack.com/services/<org_id>/<api_key>'
#         return requests.post(url, json_text, headers={"Content-type": "application/json"}).content


# debug settings

MAX_LOG_FILE_SIZE = 10 * 1024 * 1024


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    debug_mode = os.environ.get("APP_MODE", "development") == "development"

    dictConfig({
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            },
            "access": {
                "format": "%(message)s",
            }
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            # "email": {
            #     "class": "logging.handlers.SMTPHandler",
            #     "formatter": "default",
            #     "level": "ERROR",
            #     "mailhost": ("smtp.example.com", 587),
            #     "fromaddr": "devops@example.com",
            #     "toaddrs": ["receiver@example.com", "receiver2@example.com"],
            #     "subject": "Error Logs",
            #     "credentials": ("username", "password"),
            # },
            # "slack": {
            #     "class": "app.HTTPSlackHandler",
            #     "formatter": "default",
            #     "level": "ERROR",
            # },
            "service_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": "logs/service.log",
                "maxBytes": MAX_LOG_FILE_SIZE,
                "backupCount": 5,
                "delay": "True",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": "logs/error.log",
                "maxBytes": MAX_LOG_FILE_SIZE,
                "backupCount": 10,
                "delay": "True",
            },
            "access_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "access",
                "filename": "logs/access.log",
                "maxBytes": MAX_LOG_FILE_SIZE,
                "backupCount": 10,
                "delay": "True",
            }
        },
        "loggers": {
            "error": {
                "handlers": ["console"] if debug_mode else [
                    "console",
                    # "slack",
                    "error_file"
                ],
                "level": "INFO",
                "propagate": False,
            },
            "access": {
                "handlers": ["console"] if debug_mode else ["console", "access_file"],
                "level": "INFO",
                "propagate": False,
            }
        },
        "root": {
            "level": "DEBUG" if debug_mode else "INFO",
            "handlers": ["console", "service_file"] if debug_mode else [
                "console",
                # "slack"
                "service_file"
            ],
        }
    })

    logging.info(f"Setting up logging: DEBUG = {debug_mode}")
