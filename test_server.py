from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))
from auth import lambda_handler

try:
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v
except FileNotFoundError:
    print("Warning: .env file not found.")

class MockApiGateway(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        event = {
            "path": parsed.path,
            "queryStringParameters": dict(urllib.parse.parse_qsl(parsed.query))
        }
        
        response = lambda_handler(event, None)
        
        self.send_response(response.get("statusCode", 200))
        for k, v in response.get("headers", {}).items():
            self.send_header(k, v)
        self.end_headers()
        
        if "body" in response:
            self.wfile.write(response["body"].encode("utf-8"))

print("Aether Local Test Server running...")
print("Ready for Spotify OAuth. Press Ctrl+C to stop.")
HTTPServer(('127.0.0.1', 8000), MockApiGateway).serve_forever()