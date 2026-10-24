#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote, quote
import secrets, socket, os, json, mimetypes

ROOT = Path(__file__).resolve().parent
SHARED = ROOT / "shared_files"
SHARED.mkdir(exist_ok=True)
PIN = os.environ.get("TOPNOTCH_PIN") or str(secrets.randbelow(900000) + 100000)
MAX_UPLOAD = 2 * 1024 * 1024 * 1024
PAGE = (ROOT / "index.html").read_text(encoding="utf-8")

class Handler(BaseHTTPRequestHandler):
    server_version = "TopNotchShare/0.1"
    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))
    def authorized(self):
        return self.headers.get("X-TopNotch-Pin", "") == PIN
    def send_bytes(self, code, body, content_type="text/plain; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        if extra:
            for k,v in extra.items(): self.send_header(k,v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        u=urlparse(self.path); q=parse_qs(u.query)
        if u.path == "/":
            if q.get("pin", [""])[0] != PIN:
                body=("<!doctype html><meta name='viewport' content='width=device-width,initial-scale=1'><title>TOP-NOTCH SHARE PIN</title>"
                "<body style='font:16px system-ui;background:#f4f7fb;display:grid;place-items:center;min-height:90vh'><form style='background:white;padding:28px;border-radius:18px;max-width:360px;width:90%;box-shadow:0 10px 30px #0001' method='get'>"
                "<h2>TOP-NOTCH SHARE</h2><p>Enter the PIN shown on the computer running the server.</p><input name='pin' inputmode='numeric' placeholder='6-digit PIN' required style='padding:12px;width:100%;box-sizing:border-box;border:1px solid #ccd;border-radius:9px'><button style='margin-top:12px;padding:12px;width:100%;background:#5b5ce2;color:white;border:0;border-radius:9px'>Connect</button></form></body>").encode()
                self.send_bytes(200,body,"text/html; charset=utf-8"); return
            page=PAGE.replace("__PIN__",json.dumps(PIN))
            self.send_bytes(200,page.encode(),"text/html; charset=utf-8"); return
        if u.path == "/download":
            if q.get("pin",[""])[0] != PIN:
                self.send_bytes(401,b"Unauthorized"); return
            name=unquote(q.get("name",[""])[0]); p=(SHARED/name).resolve()
            if p.parent != SHARED.resolve() or not p.is_file():
                self.send_bytes(404,b"File not found"); return
            try:
                data=p.read_bytes()
                self.send_bytes(200,data,mimetypes.guess_type(p.name)[0] or "application/octet-stream",{"Content-Disposition":"attachment; filename*=UTF-8''"+quote(p.name)})
            except OSError: self.send_bytes(500,b"Could not read file")
            return
        if not self.authorized():
            self.send_bytes(401,b"Unauthorized"); return
        if u.path == "/list":
            fs=[]
            for p in sorted(SHARED.iterdir(),key=lambda p:p.name.lower()):
                if p.is_file():
                    try: fs.append({"name":p.name,"size":p.stat().st_size})
                    except OSError: pass
            self.send_bytes(200,json.dumps({"files":fs}).encode(),"application/json"); return
        self.send_bytes(404,b"Not found")
    def do_POST(self):
        u=urlparse(self.path); q=parse_qs(u.query)
        if not self.authorized():
            self.send_bytes(401,b"Unauthorized"); return
        if u.path != "/upload": self.send_bytes(404,b"Not found"); return
        try: length=int(self.headers.get("Content-Length","0"))
        except ValueError: length=0
        if length < 0 or length > MAX_UPLOAD:
            self.send_bytes(413,b"File too large (2 GB limit)"); return
        name=unquote(q.get("name",["upload.bin"])[0]).replace("\\","/").split("/")[-1].strip()
        name="".join(c for c in name if c.isprintable() and c not in '<>:"|?*')
        if not name or name in {".",".."}: name="upload.bin"
        target=SHARED/name
        if target.exists():
            stem,suffix=os.path.splitext(name); target=SHARED/f"{stem}_{secrets.token_hex(3)}{suffix}"
        remaining=length
        try:
            with target.open("wb") as out:
                while remaining:
                    chunk=self.rfile.read(min(1024*1024,remaining))
                    if not chunk: raise ConnectionError("Upload ended early")
                    out.write(chunk); remaining-=len(chunk)
            self.send_bytes(200,b"Uploaded")
            print(f"Received: {target.name} ({length} bytes)")
        except Exception as e:
            try: target.unlink(missing_ok=True)
            except Exception: pass
            self.send_bytes(500,str(e).encode())
def lan_ip():
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try: s.connect(("8.8.8.8",80)); return s.getsockname()[0]
    except OSError: return "127.0.0.1"
    finally: s.close()
if __name__=="__main__":
    port=8765
    print("\n"+"="*55+"\n TOP-NOTCH SHARE — LOCAL WI-FI STARTER\n"+"="*55)
    print(f"PIN: {PIN}")
    print(f"On this computer: http://127.0.0.1:{port}?pin={PIN}")
    print(f"On another device on the SAME Wi-Fi: http://{lan_ip()}:{port}")
    print("Enter the PIN when prompted on the other device.")
    print(f"Shared folder: {SHARED}")
    print("Trusted private Wi-Fi only. Press Ctrl+C to stop.\n"+"="*55+"\n")
    try: ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()
    except KeyboardInterrupt: print("\nTOP-NOTCH SHARE stopped.")
