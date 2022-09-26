#!/bin/env python
"""
A simple example of using Python sockets for a client HTTPS connection.
"""

import ssl
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('github.com', 443))
s = ssl.wrap_socket(s, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)
s.sendall("GET / HTTP/1.1\r\nHost: github.com\r\nConnection: close\r\n\r\n".encode())

while True:

    new = s.recv(4096)
    if not new:
      s.close()
      break
    print(new)