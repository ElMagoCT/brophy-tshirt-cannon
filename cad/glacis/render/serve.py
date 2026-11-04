"""Static server for render.html that also saves the page's POSTed PNG (POST /save?name=render.png)."""
import http.server
import os
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=HERE, **k)

    def do_POST(self):
        q = urllib.parse.urlparse(self.path)
        name = os.path.basename(urllib.parse.parse_qs(q.query).get("name", ["render.png"])[0])
        data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        with open(os.path.join(HERE, name), "wb") as fh:
            fh.write(data)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")


http.server.ThreadingHTTPServer(("127.0.0.1", 8765), H).serve_forever()
