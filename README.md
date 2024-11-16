# Requests logger

Simple python ["requests"](https://docs.python-requests.org/en/latest/index.html) logger for printing the urls, headers and bodies of request and response objects.

The library is a singleton that injects itself into the appropriate methods,
so it just needs to be imported. You can do this any way. I like this one:

```python
import importlib.util
requests_debugger = importlib.import_module("requests_debugger")
"""outputs:
requests_debugger imported
requests_debugger logger added
"""
```

If you then do something that causes requests to make an HTTP request,
it will log the url, the headers and the body (if it has a text
interpretation) to the console.

```python
import requests
x = requests.get('https://examples.http-client.intellij.net/get?generated-in=PyCharm')
"""outputs:
{
    'start': 1732038235.6376054
    'request': {
        'url': 'https://examples.http-client.intellij.net/get?generated-in=PyCharm',
        'headers': {
            'User-Agent': 'python-requests/2.32.3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        },
        'body': None,
    },
    'response': {
        'status': '200',
        'headers': {
            'Date': 'Tue, 19 Nov 2024 17:43:55 GMT',
            'Content-Type': 'application/json',
            'Transfer-Encoding': 'chunked',
            'Connection': 'keep-alive',
            'Vary': 'Accept-Encoding',
            'Access-Control-Allow-Origin':
'https://examples.http-client.intellij.net',
            'Access-Control-Allow-Credentials': 'true',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Encoding': 'gzip'
        },
        'body': {
            'args': {'generated-in': 'PyCharm'},
            'headers': {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Host': 'examples.http-client.intellij.net',
                'User-Agent': 'python-requests/2.32.3',
                'X-Forwarded-Host': 'examples.http-client.intellij.net',
                'X-Forwarded-Scheme': 'https',
                'X-Scheme': 'https'
            },
            'origin': 'x.x.x.x',
            'url':
'https://examples.http-client.intellij.net/get?generated-in=PyCharm'
        },
    }
}
"""
```



## Background

Frequently I find myself in the situation of working with a couple of layers of
3rd party packages that are making calls to an API. Under the hood they are
using the requests package which does not expose good logging or debugging
options.

The simple solution to this is to go into those libraries in your venv and
add print statements, or step through the code with a debugger. This is
time-consuming, and if the intermediate middleware is modifying requests,
such as adding auth headers, or marshalling output, can be confusing.

The solutions here are inspired by several stackoverflow question, and

There are some existing similar projects. In particular the first one which
was used as the basis for injecting logging methods:

- <https://github.com/nano-labs/requests_debugger>
- <https://github.com/mdmedley/requests_logger>

There are some other tools which expose various debugging tools for requests

- <https://pypi.org/project/requests-toolbelt/>
