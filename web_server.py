# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from threading import Thread
import json


def webServer():
    hostName = "localhost"
    serverPort = 8081

    class MyServer(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><body><h1>Hello World</h1></body></html>", "utf-8"))
        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

def start_server():
    thread = Thread(target=webServer)
    thread.start()

if __name__ == "__main__":
    start_server()