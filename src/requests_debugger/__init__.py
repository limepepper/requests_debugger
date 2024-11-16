"""Top-level package for Requests Debugger."""

__author__ = """Tom Hodder"""
__email__ = "tom@limepepper.co.uk"
__version__ = "0.1.0"

import atexit
import importlib.util
import logging
import signal
from functools import wraps

from requests.sessions import preferred_clock
from rich import inspect

from requests_debugger.debugger import _RequestsDebuggerConfig
from requests_debugger.har_creator import create_har_entry
from requests_debugger.har_model import HarEntry, Har, HarLog
from requests_debugger.request_curl import requests_to_curl

# from requests_debugger.har_model import Entry

logger = logging.getLogger(__name__)


MAX_DEPTH = 3
LOG = "log"
CURL = "curl"
REQUESTS = PYTHON = "python"
VERBOSE_FORMAT = LOG

log_methods = []
har_entries: list[HarEntry] = []


def _log_with_rich(level, message):
    if level.lower() == "error":
        console.print(f"[red][ERROR][/red] {message}")
    elif level.lower() == "warning":
        console.print(f"[yellow][WARNING][/yellow] {message}")
    else:
        print(f"calling other level with rich message")
        console.print(message)


# Check for `rich`
if importlib.util.find_spec("rich"):
    from rich.console import Console

    console = Console()
    log_methods.append(_log_with_rich)


def _log_with_loguru(_, message):
    # if hasattr(loguru_logger, level.lower()):
    #     getattr(loguru_logger, level.lower())(message)
    # else:
    loguru_logger.log("INFO", message)


if importlib.util.find_spec("loguru"):
    from loguru import logger as loguru_logger

    # log_methods.append(_log_with_loguru)


def log(level, message):
    for log_method in log_methods:
        log_method(level, message)


def _parse_response(response):
    data = {}
    if content_type := response.headers.get("Content-Type"):
        if content_type == "application/json":
            data["content"] = response.json()
    data["content_type"] = content_type
    return data


def add_logger(func):
    """this is the wrapper that should be modified to add additional logging"""

    @wraps(func)
    def logger_wrapper(*args, **kwargs):
        _args = list(args)
        logger.debug(f"args: [{_args}] kwargs: [{kwargs}]")
        req = kwargs.get("url") or _args.pop(1)
        log("info", f"{req.method}: {req.url}")
        logger.debug(f"log before calling func")
        # inspect(req)
        start = preferred_clock()
        resp = func(*args, **kwargs)
        # sockname = resp.raw._connection.sock.getsockname()
        # inspect(sockname)

        # elapsed = preferred_clock() - start
        logger.debug(f"log after calling func")
        data = _parse_response(resp)

        # print(requests_to_curl(req.method, req.url, *args, **kwargs))

        entry = create_har_entry(req, resp, start)
        har_entries.append(entry)

        message = {
            "request": {
                "method": req.method,
                "url": req.url,
                "headers": dict(req.headers),
                "body": req.body,
                "raw": req,
            },
            "response": {
                "status": resp.status_code,
                "headers": dict(resp.headers),
                "body": data.get("content"),
                "raw": resp,
            },
            "start": start,
        }

        inspect(resp)

        log("info", message)

        # har_entry = dump.dump_all(resp)
        # har_data = har_entry.decode("utf-8")
        # with open("response.har", "w") as har_file:
        #     har_file.write(har_data)
        return resp

    return logger_wrapper


def har_dump(message: str = None):
    har = Har(log=HarLog(entries=debug_requests.har_entries))
    har_as_dict = har.to_dict()
    # inspect(har_as_dict)
    import json

    with open("output.har", "w") as f:
        f.write(
            json.dumps(
                har_as_dict,
                indent=2,
            ),
        )
    print(f"har dumped {message}")


print("requests_debugger imported")
debug_requests = _RequestsDebuggerConfig(add_logger)
debug_requests.set_entries(har_entries)
print("requests_debugger logger added")

atexit.register(har_dump)

signal.signal(signal.SIGINT, lambda signum, frame: har_dump("sigint"))
signal.signal(signal.SIGTERM, lambda signum, frame: har_dump("sigterm"))
