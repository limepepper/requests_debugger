# import pprint
from rich.console import Console
import http.client as http_client
from http.client import HTTPConnection

console = Console()

import http.client as http_client

# Enable debugging at http.client level (prints request and response details)
http_client.HTTPConnection.debuglevel = 2


import logging


# Create custom HTTPConnection with body logging
class DebuggingHTTPConnection(HTTPConnection):
    def send(self, data):
        if self.debuglevel > 0:
            print(f'--->SENT DATA:\n{data.decode("utf-8")}\n---')
        super().send(data)

    def putheader(self, header, *values):
        if self.debuglevel > 0:
            print(f"--->HEADER: {header}: {values}")
        super().putheader(header, *values)


def stuff():
    # Configure logging
    logging.basicConfig(level=1)
    logging.getLogger("urllib3").setLevel(1)
    logging.getLogger("requests").setLevel(1)

    # Optional: Log to a file instead of the console
    file_handler = logging.FileHandler("requests.log")
    logging.getLogger("urllib3").addHandler(file_handler)

    # Create detailed formatter
    formatter2 = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    # Setup file handler
    file_handler2 = logging.FileHandler("api_debug.log")
    file_handler2.setFormatter(formatter2)
    file_handler2.setLevel(logging.DEBUG)

    logging.basicConfig(level=logging.DEBUG, handlers=[file_handler2])

    for name in ["urllib3", "requests"]:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler2)

    http_client.HTTPConnection = DebuggingHTTPConnection
    http_client.HTTPConnection.debuglevel = 2


# Log HTTP response bodies
def log_response_body(response, *args, **kwargs):
    logger = logging.getLogger("requests.packages.urllib3")
    logger.debug(f"Response body: {response.text}")


# Add response hook to requests

# requests.hooks["response"].append(log_response_body)
