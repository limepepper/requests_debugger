import importlib
import json
import urllib.error
import urllib.parse
import urllib.request
from functools import wraps

from rich import inspect
from rich import print as rprint
from rich.pretty import pprint

from requests_debugger.debugger import _RequestsDebuggerConfig


def requests_to_curl(method, url, *args, **kwargs):
    """Return the request as cURL string."""
    print(f"requests_to_curl args: [{args}] kwargs: [{kwargs}]")
    data = args[1]
    kwargs = {
        "headers": data.headers,
        "cookies": data._cookies,
    }

    lines = []
    lines += [
        '-H "%s: %s"' % (k, v) for k, v in list(kwargs.get("headers", {}).items())
    ]
    # cookies = [
    #     '-H "cookie: %s=%s"' % (k, v)
    #     for k, v in list(kwargs.get("cookies", {}).items())
    # ]
    # headers = " \\\n".join(headers + cookies)
    params = urllib.parse.urlencode(kwargs.get("params", ""))

    body = kwargs.get("data") or kwargs.get("json")
    if isinstance(body, dict):
        body = json.dumps(body)
    if body:
        lines += "-d '%s'" % body

    proxies = kwargs.get("proxies") or {}
    lines += " ".join(
        ["--proxy %s://%s" % (proto, uri) for proto, uri in list(proxies.items())]
    )

    if params:
        url = "%s%s%s" % (url, "&" if "?" in url else "?", params)

    curl = f"""
    curl {url} \\
        -X {method.upper()} \\
"""
    for i, header in enumerate(lines):
        curl += f"        {header}"
        curl += " \\\n" if i < len(lines) - 1 else "\n"
    # if body:
    #     curl += f"        {body} \\\n"
    # if proxies:
    #     curl += f"        {proxies} \\\n"

    return curl
