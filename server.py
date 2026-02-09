from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
import os
import time

GPS_FILE = "gps.json"
REQUESTS_FILE = "requests.json"
EXPIRATION_TIME = 10


class MyHandler(SimpleHTTPRequestHandler):

    # ✅ 모든 요청 로그 찍기
    def log_message(self, format, *args):
        return  # 기본 http 로그 제거 (우리가 직접 로그 찍을 것)

    def log_request_info(self, tag):
        print(f"[{tag}] IP:{self.client_address[0]} PATH:{self.path}")

    # ---------------- GET ----------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.path = "/index.html"

        elif path.startswith("/driver"):
            self.path = "/driver.html"

        elif path.startswith("/admin"):
            self.path = "/admin.html"

        # ✅ GPS 반환
        elif path == "/gps":
            self.log_request_info("GET /gps")

            gps_dict = {}
            if os.path.exists(GPS_FILE):
                with open(GPS_FILE, "r", encoding="utf-8") as f:
                    try:
                        gps_dict = json.load(f)
                    except:
                        gps_dict = {}

            # 만료 필터링
            now = time.time()
            valid_gps = {}
            is_changed = False

            for dev_id, info in gps_dict.items():
                if now - info.get("last_seen", 0) < EXPIRATION_TIME:
                    valid_gps[dev_id] = info
                else:
                    is_changed = True

            if is_changed:
                with open(GPS_FILE, "w", encoding="utf-8") as f:
                    json.dump(valid_gps, f, ensure_ascii=False)

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(valid_gps, ensure_ascii=False).encode('utf-8'))
            return

        # ✅ 호출 리스트
        elif path == "/list":
            self.log_request_info("GET /list")

            if os.path.exists(REQUESTS_FILE):
                with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
                    list_data = f.read()
            else:
                list_data = "[]"

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(list_data.encode('utf-8'))
            return

        return SimpleHTTPRequestHandler.do_GET(self)

    # ---------------- POST ----------------
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except:
            self.send_response(400)
            self.end_headers()
            return

        # ✅ GPS 수신
        if self.path == "/gps":
            device_id = data.get("deviceId")
            driver_name = data.get("id")
            lat = data.get("lat")
            lng = data.get("lng")

            print(f"[POST /gps] deviceId:{device_id} name:{driver_name} lat:{lat} lng:{lng}")

            if not device_id:
                self.send_response(400)
                self.end_headers()
                return

            gps_dict = {}
            if os.path.exists(GPS_FILE):
                with open(GPS_FILE, "r", encoding="utf-8") as f:
                    try:
                        gps_dict = json.load(f)
                    except:
                        pass

            gps_dict[device_id] = {
                "id": driver_name,
                "lat": lat,
                "lng": lng,
                "last_seen": time.time()
            }

            with open(GPS_FILE, "w", encoding="utf-8") as f:
                json.dump(gps_dict, f, ensure_ascii=False)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

        # ✅ 호출 저장
        elif self.path == "/request":
            print(f"[POST /request] {data}")

            from_addr = data.get("from")
            to_addr = data.get("to")
            phone = data.get("phone")

            req_list = []
            if os.path.exists(REQUESTS_FILE):
                with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
                    try:
                        req_list = json.load(f)
                    except:
                        pass

            req_list.append({"from": from_addr, "to": to_addr, "phone": phone})

            with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
                json.dump(req_list, f, ensure_ascii=False)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(" 호출이 완료되었습니다.".encode('utf-8'))
            return

        # ✅ 완료 처리
        elif self.path == "/done":
            print(f"[POST /done] index:{data.get('index')}")

            idx = data.get("index")

            if os.path.exists(REQUESTS_FILE):
                with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
                    try:
                        req_list = json.load(f)
                        idx_int = int(idx)

                        if 0 <= idx_int < len(req_list):
                            req_list.pop(idx_int)

                            with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
                                json.dump(req_list, f, ensure_ascii=False)

                            self.send_response(200)
                            self.end_headers()
                            return
                    except:
                        pass

            self.send_response(400)
            self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), MyHandler)
    print("✅ Server started at http://localhost:8000")
    server.serve_forever()
