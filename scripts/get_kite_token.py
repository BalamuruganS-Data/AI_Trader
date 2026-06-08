import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from kiteconnect import KiteConnect

API_KEY = "eh0liyrp1js4nzbk"
API_SECRET = "sq8q3fasf1zw8isqfxtjoxcrez89hyav"
REDIRECT_HOST = "127.0.0.1"
REDIRECT_PORT = 8000
REDIRECT_PATH = "/kite_callback"
REDIRECT_URL = f"http://{REDIRECT_HOST}:{REDIRECT_PORT}{REDIRECT_PATH}"
SESSION_FILE = "kite_session.json"


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        if "request_token" in query:
            request_token = query["request_token"][0]
            self.server.request_token = request_token
            self.wfile.write(b"<html><body><h1>Request token received.</h1><p>You can close this window.</p></body></html>")
        else:
            self.wfile.write(b"<html><body><h1>No request_token found.</h1><p>Check the redirect URL and login again.</p></body></html>")

    def log_message(self, format, *args):
        return


def main():
    kite = KiteConnect(api_key=API_KEY)
    login_url = kite.login_url()

    print("Open this URL in a browser and complete login:")
    print(login_url)
    webbrowser.open(login_url)
    print(f"Waiting for Kite to redirect to {REDIRECT_URL}...")

    server = HTTPServer((REDIRECT_HOST, REDIRECT_PORT), RequestHandler)
    server.handle_request()

    request_token = getattr(server, "request_token", None)
    if not request_token:
        print("No request_token received. Make sure your Kite app redirect URL is set to:")
        print(REDIRECT_URL)
        return

    print("Request token received. Exchanging for access token...")
    session_data = kite.generate_session(request_token, api_secret=API_SECRET)
    session_data["redirect_url"] = REDIRECT_URL
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, default=str)

    print("Saved Kite session to", SESSION_FILE)
    print("Update your config.py with BROKER['access_token'] and BROKER['user_id'] from this file.")
    print(json.dumps(session_data, indent=2, default=str))


if __name__ == "__main__":
    main()
