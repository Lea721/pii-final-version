# from http_server import HTTPServer

from http_server import HTTPServer
import json

# Load paths from JSON file
with open('paths.json', 'r') as f:
    paths = json.load(f)

server = HTTPServer('localhost', 8000, paths)
server.run_server()
