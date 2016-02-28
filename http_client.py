import usocket
import ujson
try:
    import ussl
except ImportError:
    ussl = None

CONTENT_TYPE_JSON = "application/json"


class Response(object):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    @property
    def text(self, encoding='utf-8'):
        return self.content.decode(encoding)

    def json(self):
        return ujson.loads(self.content)

    def raise_for_status(self):
        if 400 <= self.status_code < 500:
            raise OSError('Client error: %s' % self.status_code)
        if 500 <= self.status_code < 600:
            raise OSError('Server error: %s' % self.status_code)


# Adapted from upip
def request(method, url, json=None, timeout=None, headers=None):
    urlparts = url.split('/', 3)
    proto = urlparts[0]
    host = urlparts[2]
    urlpath = '' if len(urlparts) < 4 else urlparts[3]

    if proto == 'http:':
        port = 80
    elif proto == 'https:':
        port = 443
    else:
        raise OSError('Unsupported protocol: %s' % proto[:-1])

    if ':' in host:
        host, port = host.split(':')
        port = int(port)

    if json is not None:
        content = ujson.dumps(json)
        content_type = CONTENT_TYPE_JSON
    else:
        content = None

    ai = usocket.getaddrinfo(host, port)
    addr = ai[0][4]

    sock = usocket.socket()

    if timeout is not None:
        assert hasattr(sock, 'settimeout'), 'Socket does not support timeout'
        sock.settimeout(timeout)

    try:
        sock.connect(addr)

        if proto == 'https:':
            assert ussl is not None, 'HTTPS not supported: could not find ussl'
            sock = ussl.wrap_socket(sock)

        # MicroPython rawsocket module supports file interface directly
        sock.write('%s /%s HTTP/1.0\r\nHost: %s\r\n' % (method, urlpath, host))

        if headers is not None:
            for header in headers.items():
                sock.write('%s: %s\r\n' % header)

        if content is not None:
            sock.write('content-length: %s\r\n' % len(content))
            sock.write('content-type: %s\r\n' % content_type)
            sock.write('\r\n')
            sock.write(content)
        else:
            sock.write('\r\n')

        l = sock.readline()
        protover, status, msg = l.split(None, 2)

        # Skip headers
        while sock.readline() != b'\r\n':
            pass

        content = b''

        while 1:
            l = sock.read(1024)
            if not l:
                break
            content += l

        return Response(int(status), content)
    finally:
        sock.close()


def get(url, **kwargs):
    return request('GET', url, **kwargs)


def post(url, **kwargs):
    return request('POST', url, **kwargs)


def support_ssl():
    return ussl is not None


def support_timeout():
    return hasattr(usocket.socket, 'settimeout')
