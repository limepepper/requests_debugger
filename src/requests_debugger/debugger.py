import requests

from requests_debugger.har_model import HarEntry, Har, HarLog
from contextlib import contextmanager
import logging

logger = logging.getLogger("requests_debugger")


class _RequestsDebuggerConfig:
    def __init__(self, wrapper):

        self.debug_requests = False
        self.wrapper = wrapper
        self.har_entries: list[HarEntry] = []

        self._apply()

    def _apply(self):
        inject_point = requests.Session
        method = "send"
        self._patch(inject_point, method, self.wrapper)

    @contextmanager
    def context_thing(self):
        # print(f"_apply output_format {output_format} max_depth {max_depth}")
        # for inject_point in [requests, requests.Session]:
        #     for method in ["get", "post", "put", "patch", "delete"]:
        #         _patch(inject_point, method, add_logger)
        # method = "request"
        # inject_point = requests.Session
        try:
            print("Background logging started.")
            logger.info("Background logging started.")
            inject_point = requests.Session
            method = "send"
            self._patch(inject_point, method, self.wrapper)
            yield
        finally:
            print("got here")
            self._har_dump("finalized")
            logger.info("Background logging finalized.")

    def _har_dump(self, message: str = None):
        har = Har(log=HarLog(entries=self.har_entries))
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

    def _patch(self, inject_point, method, wrapper):
        func = getattr(inject_point, "_%s" % method, getattr(inject_point, method))
        setattr(inject_point, "_%s" % method, func)
        logged_func = wrapper(func)
        setattr(inject_point, method, logged_func)

        # FIXME unpatch

    def set_entries(self, har_entries):
        self.har_entries = har_entries
