#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json

results = [
    {
        "id": "111aaaaaa",
        "rssi": -65,
        "connectable": False,
        "company": "Samsung"
    },
    {
        "id": "2222bbbbbb",
        "rssi": -75,
        "connectable": True,
        "company": "Apple"
    },
    {
        "id": "3333cccccc",
        "rssi": -44,
        "connectable": True,
        "company": "Nokia"
    }
]

devices = []

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(devices).encode())
        return

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        data = self.rfile.read(int(self.headers['Content-Length']))
        json_data = json.loads(data)
        devices.append(json_data)
        return

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), RequestHandler)
    print('Starting server at http://localhost:8000')
    server.serve_forever()