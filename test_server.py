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
    pass

class MockApiGateway(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.end_headers()

    def handle_request(self, method):
        parsed = urllib.parse.urlparse(self.path)
        headers_dict = {k: v for k, v in self.headers.items()}
        
        body_data = "{}"
        if method == "POST":
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body_data = self.rfile.read(content_length).decode('utf-8')

        event = {
            "path": parsed.path,
            "httpMethod": method,
            "queryStringParameters": dict(urllib.parse.parse_qsl(parsed.query)),
            "headers": headers_dict,
            "body": body_data
        }
        
        response = lambda_handler(event, None)
        
        self.send_response(response.get("statusCode", 200))
        for k, v in response.get("headers", {}).items():
            self.send_header(k, v)
        self.end_headers()
        
        if "body" in response:
            self.wfile.write(response["body"].encode("utf-8"))

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

print("Aether API Gateway Mock Server running at http://127.0.0.1:8000")
print("Press Ctrl+C to safely terminate.")
HTTPServer(('127.0.0.1', 8000), MockApiGateway).serve_forever()