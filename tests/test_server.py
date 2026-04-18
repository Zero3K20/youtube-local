import importlib.util
import pathlib
import socket
import sys
import types
import urllib3


def load_server_module(monkeypatch):
    monkeypatch.setattr(socket, 'socket', socket.SocketType)

    gevent_module = types.ModuleType('gevent')
    gevent_monkey = types.ModuleType('gevent.monkey')
    gevent_socket = types.ModuleType('gevent.socket')
    gevent_pywsgi = types.ModuleType('gevent.pywsgi')
    gevent_monkey.patch_all = lambda: None
    gevent_pywsgi.WSGIServer = object
    gevent_module.monkey = gevent_monkey
    gevent_module.socket = gevent_socket
    monkeypatch.setitem(sys.modules, 'gevent', gevent_module)
    monkeypatch.setitem(sys.modules, 'gevent.monkey', gevent_monkey)
    monkeypatch.setitem(sys.modules, 'gevent.socket', gevent_socket)
    monkeypatch.setitem(sys.modules, 'gevent.pywsgi', gevent_pywsgi)

    youtube_module = types.ModuleType('youtube')
    youtube_module.yt_app = lambda env, start_response: []
    youtube_util = types.ModuleType('youtube.util')
    youtube_util.fetch_url_response = None
    youtube_module.util = youtube_util
    monkeypatch.setitem(sys.modules, 'youtube', youtube_module)
    monkeypatch.setitem(sys.modules, 'youtube.util', youtube_util)
    for name in (
        'youtube.watch',
        'youtube.search',
        'youtube.playlist',
        'youtube.channel',
        'youtube.local_playlist',
        'youtube.comments',
        'youtube.subscriptions',
    ):
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))

    module_path = pathlib.Path(__file__).parent.parent / 'server.py'
    spec = importlib.util.spec_from_file_location('server_for_test', module_path)
    server_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_module)
    return server_module


class MockResponse:
    def __init__(self, parts, content_length):
        self.parts = list(parts)
        self.headers = {'Content-Length': str(content_length)}
        self.status = 200
        self.reason = 'OK'

    def read(self, _amount):
        part = self.parts.pop(0)
        if isinstance(part, Exception):
            raise part
        return part


def test_proxy_site_retries_on_read_timeout(monkeypatch):
    server = load_server_module(monkeypatch)
    request_headers = []
    request_kwargs = []
    responses = [
        MockResponse(
            [
                b'abc',
                urllib3.exceptions.ReadTimeoutError(None, None,
                                                    'Read timed out.'),
            ],
            6,
        ),
        MockResponse([b'def', b''], 3),
    ]

    def mock_fetch_url_response(_url, send_headers, *args, **kwargs):
        request_headers.append(dict(send_headers))
        request_kwargs.append(dict(kwargs))
        return responses.pop(0), (lambda _response: None)

    monkeypatch.setattr(server.util, 'fetch_url_response', mock_fetch_url_response)
    monkeypatch.setattr(server.time, 'sleep', lambda _seconds: None)

    response_meta = {}

    def start_response(status, headers):
        response_meta['status'] = status
        response_meta['headers'] = headers

    env = {
        'PATH_INFO': '/videoplayback',
        'QUERY_STRING': '',
        'SERVER_NAME': 'rr3---sn-5ualdnss.googlevideo.com',
    }

    body = b''.join(server.proxy_site(env, start_response, video=True))

    assert body == b'abcdef'
    assert response_meta['status'] == '200 OK'
    assert request_headers[1]['Range'] == 'bytes=3-5'
    assert request_kwargs[0]['timeout'] == 45
