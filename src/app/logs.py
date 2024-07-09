import logging
import sys
from typing import Callable

from fastapi import Request, Response


class ErrorCheckHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_occurred = False

    def emit(self, record):
        if record.levelno == logging.ERROR:
            self.error_occurred = True
        # we don't want to emit anything, as that is handle by the click handler,
        # so do not call super
        # super().emit(record)


class CustomLogger(logging.Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_handler = JsonHandler()
        self.addHandler(self.json_handler)

    @property
    def error_occurred(self) -> bool:
        return any(
            handler.error_occurred
            for handler in self.handlers
            if isinstance(handler, ErrorCheckHandler)
        )

    def get_logs(self):
        return self.json_handler.get_logs()

    def clear_logs(self):
        self.json_handler.clear_logs()


class JsonHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_records = []

    def emit(self, record):
        self.log_records.append(record.__dict__)

    def get_logs(self):
        return self.log_records

    def clear_logs(self):
        self.log_records = []


async def add_json_handler(request: Request, call_next: Callable) -> Response:
    logging.setLoggerClass(CustomLogger)
    logger = CustomLogger(f"labbox-logger{id(request)}")

    error_check_handler = ErrorCheckHandler(stream=sys.stderr)

    logger.addHandler(error_check_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = True

    request.state.logger = logger

    response: Response = await call_next(request)

    logger.clear_logs()  # Clear the logs after each request

    return response


# logging.setLoggerClass(CustomLogger)
# logger = logging.getLogger("labbox-logger")

# error_check_handler = ErrorCheckHandler(stream=sys.stderr)

# logger.addHandler(error_check_handler)
# logger.setLevel(logging.INFO)
# logger.propagate = True
