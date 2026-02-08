from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import os

GPS_FILE = "gps.json"
REQUESTS_FILE = "requests.json"

class MyHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith("/driver"):
            self.path = "/driver.html"

        elif self.path.startswith("/admin"):
            self.path = "/admin.html"

        elif self.path == "/gps":
            # GPS 위치 데이터 반환
            if os.path.exists(GPS_FILE):
                with open(GPS_FILE, "r", encoding="utf-8") as f:
                    gps_data = f.read()
            else:
                gps_data = "{}"  # 빈 JSON 객체

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(gps_data.encode('utf-8'))
            return

        elif self.path == "/list":
            # 택시 호출 목록 데이터 반환
            if os.path.exists("requests.json"):
                with open("requests.json", "r", encoding="utf-8") as f:
                    list_data = f.read()
            else:
                list_data = "[]"  # 빈 배열

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(list_data.encode('utf-8'))
            return

        # 위에서 처리하지 않은 요청은 기본 파일 서버 처리
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON format")
            return

        if self.path == "/gps":
            driver_id = data.get("id")
            lat = data.get("lat")
            lng = data.get("lng")

            if not driver_id or lat is None or lng is None:
                self.send_response(400)
                self.end_headers()
                self.wfile.write("필수 정보 누락".encode('utf-8'))
                return

            if os.path.exists(GPS_FILE):
                with open(GPS_FILE, "r", encoding="utf-8") as f:
                    gps_data = json.load(f)
            else:
                gps_data = {}

            gps_data[driver_id] = {"lat": lat, "lng": lng}

            with open(GPS_FILE, "w", encoding="utf-8") as f:
                json.dump(gps_data, f, ensure_ascii=False)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
            return

        elif self.path == "/request":
            from_addr = data.get("from")
            to_addr = data.get("to")
            phone = data.get("phone")

            if not from_addr or not to_addr or not phone:
                self.send_response(400)
                self.end_headers()
                self.wfile.write("모든 항목을 입력해주세요.".encode('utf-8'))
                return

            if os.path.exists(REQUESTS_FILE):
                with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
                    req_list = json.load(f)
            else:
                req_list = []

            req_list.append({"from": from_addr, "to": to_addr, "phone": phone})

            with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
                json.dump(req_list, f, ensure_ascii=False)

            self.send_response(200)
            self.end_headers()
            self.wfile.write("택시 호출이 완료되었습니다.".encode('utf-8'))
            return

        elif self.path == "/done":
            idx = data.get("index")
            if idx is None:
                self.send_response(400)
                self.end_headers()
                self.wfile.write("index 필수".encode('utf-8'))
                return

            if os.path.exists(REQUESTS_FILE):
                with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
                    req_list = json.load(f)
            else:
                req_list = []

            try:
                idx_int = int(idx)
                if 0 <= idx_int < len(req_list):
                    req_list.pop(idx_int)
                    with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
                        json.dump(req_list, f, ensure_ascii=False)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write("완료 처리되었습니다.".encode('utf-8'))
                    
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write("인덱스 범위 오류".encode('utf-8'))
                    
            except Exception:
                self.send_response(400)
                self.end_headers()
                self.wfile.write("잘못된 인덱스".encode('utf-8'))
                
            return

        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), MyHandler)
    print("Server started at http://0.0.0.0:8000")
    server.serve_forever()