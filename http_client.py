import usocket


class Response(object):
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    @property
    def text(self, encoding='utf-8'):
        return self.content.decode(encoding)

    def json(self):
        import ujson
        return ujson.loads(self.content)

    def raise_for_status(self):
        if 400 <= self.status_code < 500:
            raise OSError('Client error: %s' % self.status_code)
        if 500 <= self.status_code < 600:
            raise OSError('Server error: %s' % self.status_code)


# Adapted from upip
def request(method, url, content=None):
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

    ai = usocket.getaddrinfo(host, port)
    addr = ai[0][4]

    s = usocket.socket()
    try:
        s.connect(addr)

        if proto == 'https:':
            import ussl
            s = ussl.wrap_socket(s)

        # MicroPython rawsocket module supports file interface directly
        s.write('%s /%s HTTP/1.0\r\nHost: %s\r\n' % (method, urlpath, host))

        if content is not None:
            s.write('content-length: %s\r\n' % len(content))
            s.write('\r\n')
            s.write(content)
        else:
            s.write('\r\n')

        l = s.readline()
        protover, status, msg = l.split(None, 2)

        # Skip headers
        while s.readline() != b'\r\n':
            pass

        content = b''

        while 1:
            l = s.read(1024)
            if not l:
                break
            content += l

        return Response(int(status), content)
    finally:
        s.close()


def get(url):
    return request('GET', url)


def post(url, content):
    return request('POST', url, content)
