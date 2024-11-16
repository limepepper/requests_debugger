from dataclasses import asdict
from datetime import datetime, timezone
import json
from typing import Any, Dict
from urllib.parse import parse_qsl, urlparse

import requests
from requests import PreparedRequest, Response

from .har_model import (
    Har,
    HarLog,
    HarEntry,
    HarRequest,
    HarResponse,
    HarCookie,
    HarPostData,
    HarContent,
    HarTimings,
)


def _parse_headers(headers: Dict[str, str]) -> list[dict]:
    return [{"name": name, "value": value} for name, value in headers.items()]


def _parse_cookies(cookies: Dict[str, str]) -> list[HarCookie]:
    return [
        HarCookie(
            name=name,
            value=value,
            path="/",
            domain="",
            expires="",
            http_only=False,
            secure=False,
        )
        for name, value in cookies.items()
    ]


def _parse_query_string(url: str) -> list[dict]:
    parsed = urlparse(url)
    return [{"name": name, "value": value} for name, value in parse_qsl(parsed.query)]


def _parse_post_data(body: str) -> HarPostData:
    return HarPostData(
        text=body,
        params=[],
        mime_type="application/x-www-form-urlencoded",
        comment="",
    )


def create_request_entry(req: Any) -> HarRequest:
    return HarRequest(
        method=req.method,
        url=req.url,
        http_version="HTTP/1.1",
        cookies=_parse_cookies(dict(req._cookies)),
        headers=_parse_headers(dict(req.headers)),
        query_string=_parse_query_string(req.url),
        post_data=_parse_post_data(req.body) if req.body else None,
        headers_size=-1,
        body_size=len(req.body) if req.body else 0,
    )


def _parse_content(resp: Any) -> HarContent:
    return HarContent(
        size=len(resp.content),
        mime_type=resp.headers.get("content-type", ""),
        text=resp.text,
        compression=0,
        comment="",
    )


def create_response_entry(resp: Any) -> HarResponse:
    content = {
        "size": len(resp.content),
        "mimeType": resp.headers.get("content-type", ""),
        "text": resp.text,
    }

    return HarResponse(
        status=resp.status_code,
        status_text=resp.reason,
        http_version="HTTP/1.1",
        cookies=_parse_cookies(dict(resp.cookies)),
        headers=_parse_headers(dict(resp.headers)),
        content=_parse_content(resp),
        redirect_url=resp.headers.get("location", ""),
        headers_size=-1,
        body_size=len(resp.content),
        comment="",
    )


def create_har_entry(
    req: PreparedRequest, resp: Response, start_time: float
) -> HarEntry:

    return HarEntry(
        started_date_time=datetime.fromtimestamp(start_time, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ",
        ),
        time=resp.elapsed.total_seconds() * 1000,
        request=create_request_entry(req),
        response=create_response_entry(resp),
        cache={},
        timings=HarTimings(
            # connect=0,
            send=0,
            wait=resp.elapsed.total_seconds() * 1000,
            receive=0,
        ),
        server_ip="",
        connection="",
        comment="",
        cookies=[],
    )


def create_har(entries: list[HarEntry]) -> Har:
    return Har(log=HarLog(entries=entries))


def serialize_to_har(entries: list[HarEntry]) -> str:
    har = create_har(entries)
    return json.dumps(asdict(har), indent=2)
