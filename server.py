from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import os
import time  # [수정] 시간 계산을 위해 추가

GPS_FILE = "gps.json"
REQUESTS_FILE = "requests.json"
EXPIRATION_TIME = 10  # [수정] 10초 동안 소식 없으면 삭제

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.path = "/index.html"
        elif self.path.startswith("/driver"):
            self.path = "/driver.html"
        elif self.path.startswith("/admin"):
            self.path = "/admin.html"
        
        # GPS 데이터 반환 (필터링 로직 추가)
        elif self.path == "/gps": # [수정] 도메인 제거, 상대경로로 처리
            gps_dict = {}
            if os.path.exists(GPS_FILE):
                with open(GPS_FILE, "r", encoding="utf-8") as f:
                    try: gps_dict = json.load(f)
                    except: gps_dict = {}
            
            # [수정] 만료된 기기 삭제 로직
            now = time.time()
            valid_gps = {}
            is_changed = False
            for dev_id, info in gps_dict.items():
                # 마지막 업데이트 시간이 10초 이내인 경우만 유지
                if now - info.get("last_seen", 0) < EXPIRATION_TIME:
                    valid_gps[dev_id] = info
                else:
                    is_changed = True
            
            # 삭제된 데이터가 있다면 파일 갱신
            if is_changed:
                with open(GPS_FILE, "w", encoding="utf-8") as f:
                    json.dump(valid_gps, f, ensure_ascii=False)

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(valid_gps, ensure_ascii=False).encode('utf-8'))
            return

        elif self.path == "/list":
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

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
        except:
            self.send_response(400); self.end_headers(); return

        if self.path == "/gps": # [수정] 도메인 제거
            device_id = data.get("deviceId")
            driver_name = data.get("id")
            lat = data.get("lat")
            lng = data.get("lng")
            if not device_id:
                self.send_response(400); self.end_headers(); return

            gps_dict = {}
            if os.path.exists(GPS_FILE):
                with open(GPS_FILE, "r", encoding="utf-8") as f:
                    try: gps_dict = json.load(f)
                    except: pass
            
            # [수정] 저장할 때 현재 서버 시간(last_seen)을 기록
            gps_dict[device_id] = {
                "id": driver_name, 
                "lat": lat, 
                "lng": lng,
                "last_seen": time.time() 
            }
            with open(GPS_FILE, "w", encoding="utf-8") as f:
                json.dump(gps_dict, f, ensure_ascii=False)

            self.send_response(200); self.end_headers()
            self.wfile.write(b"OK")

        elif self.path == "/request":
            # ... (호출 저장 로직 동일)
            from_addr = data.get("from"); to_addr = data.get("to"); phone = data.get("phone")
            req_list = []
            if os.path.exists(REQUESTS_FILE):
                with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
                    try: req_list = json.load(f)
                    except: pass
            req_list.append({"from": from_addr, "to": to_addr, "phone": phone})
            with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
                json.dump(req_list, f, ensure_ascii=False)
            self.send_response(200); self.end_headers()
            self.wfile.write(" 호출이 완료되었습니다.".encode('utf-8'))

        elif self.path == "/done":
            # ... (완료 처리 로직 동일)
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
                            self.send_response(200); self.end_headers(); return
                    except: pass
            self.send_response(400); self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), MyHandler)
    print("Server started at http://localhost:8000")
    server.serve_forever()
