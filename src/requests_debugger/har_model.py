from dataclasses import dataclass, field

from requests_debugger.har_mixin import (
    HarMixin,
)


@dataclass
class HarCreator:
    name: str = "Requests Debugger"
    version: str = "0.1.0"
    comment: str = ""


@dataclass
class HarBrowser:
    name: str = "Requests Debugger"
    version: str = "0.1.0"
    comment: str = ""


@dataclass
class HarPage:
    started_date_time: str
    id: str
    title: str
    page_timings: dict


@dataclass
class HarCookie:
    name: str
    value: str
    path: str
    domain: str
    expires: str
    http_only: bool
    secure: bool


@dataclass
class HarParams:
    name: str
    value: str | None
    file_name: str | None
    content_type: str | None
    comment: str = ""


@dataclass
class HarPostData:
    text: str
    params: list[HarParams]
    mime_type: str
    comment: str


@dataclass
class HarHeader:
    name: str
    value: str
    comment: str


@dataclass
class HarContent:
    size: int
    mime_type: str = field(metadata={"field_name": "mimeType"})
    text: str | None
    compression: int | None
    comment: str = ""


@dataclass
class HarRequest:
    method: str
    url: str
    http_version: str
    cookies: list[HarCookie]
    headers: list[HarHeader]
    query_string: list[dict]
    post_data: HarPostData | None
    headers_size: int
    body_size: int


@dataclass
class HarResponse:
    status: int
    status_text: str
    http_version: str
    cookies: list[HarCookie]
    headers: list[HarHeader]
    content: HarContent
    redirect_url: str = field(metadata={"field_name": "redirectURL"})
    headers_size: int
    body_size: int
    comment: str = ""


@dataclass
class HarTimings:
    """
        http://www.softwareishard.com/blog/har-12-spec/#timings

    The send, wait and receive timings are not optional and must have non-negative values.

    An exporting tool can omit the blocked, dns, connect and ssl, timings on every request if it is unable to provide them. Tools that can provide these timings can set their values to -1 if they don’t apply. For example, connect would be -1 for requests which re-use an existing connection.

    The time value for the request must be equal to the sum of the timings supplied in this section (excluding any -1 values).

    Following must be true in case there are no -1 values (entry is an object in log.entries) :
    entry.time == entry.timings.blocked + entry.timings.dns +
        entry.timings.connect + entry.timings.send + entry.timings.wait +
        entry.timings.receive;

        /// http.client.HTTPConnection.debuglevel = 1

    """

    send: float
    wait: float
    receive: float
    blocked: float = -1
    dns: float = -1
    connect: float = -1
    ssl: float = -1
    comment: str = ""

    def validate(self):
        # The send, wait and receive timings are not optional and must have non-negative values.
        if self.send < 0:
            return False
        if self.wait < 0:
            return False
        if self.receive < 0:
            return False


@dataclass
class HarEntry(HarMixin):
    started_date_time: str = field(metadata={"name": "startedDateTime"})
    time: float
    request: HarRequest
    response: HarResponse
    cache: dict
    timings: HarTimings
    server_ip: str = field(metadata={"field_name": "serverIPAddress"})
    connection: str
    comment: str
    cookies: list[HarCookie]

    def validate(self):
        # fmt: off
        if (
            self.time
            != self.timings.send
            + self.timings.wait
            + self.timings.receive
            + (self.timings.dns if self.timings.dns != -1 else 0)
            + (self.timings.connect if self.timings.connect != -1 else 0)
            + (self.timings.blocked if self.timings.blocked != -1 else 0)
        ):
            return False
        # fmt: on

        return True


@dataclass
class HarLog:
    version: str = "1.2"
    creator: HarCreator = field(default_factory=HarCreator)
    browser: HarBrowser = field(default_factory=HarBrowser)
    pages: list[HarPage] = field(default_factory=list)
    entries: list[HarEntry] = field(default_factory=list)
    comment: str = ""


@dataclass
class Har(HarMixin):
    log: HarLog

    # def to_json(self, include_null=False) -> dict:
