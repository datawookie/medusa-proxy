#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep

HTML_FILE_NAME = 'proxy-list.txt'
PORT_NUMBER = 8800

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.path = HTML_FILE_NAME
        try:
            with open(curdir + sep + self.path, 'r') as f:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(bytes(f.read(), 'UTF-8'))
            return
        except IOError:
            self.send_error(404, 'File Not Found: %s.' % self.path)

print('Started HTTP server on port %i.' % PORT_NUMBER)
server = HTTPServer(('', PORT_NUMBER), Handler).serve_forever()
