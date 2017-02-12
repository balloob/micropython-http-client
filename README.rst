MicroPython HTTP Client
=======================

## Deprecated. Please use the built-in one now that it's available.

HTTP 1.0 client for MicroPython with a small subset of the API of `Requests for Humans <https://github.com/kennethreitz/requests>`_. Please note that it does not verify SSL certificates.

.. code-block:: python

    import http_client

    r = http_client.get('http://httpbin.org/get')
    r.raise_for_status()
    print(r.status_code)
    print(r.text)  # r.content for raw bytes

    r = http_client.post('http://httpbin.org/post', json={'hello': 'world'})
    print(r.json())

