from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import os

GPS_FILE = "gps.json"
REQUESTS_FILE = "requests.json"

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # 경로 처리
        if self.path == "/" or self.path == "/index.html":
            self.path = "/index.html"
        elif self.path.startswith("/driver"):
            self.path = "/driver.html"
        elif self.path.startswith("/admin"):
            self.path = "/admin.html"
        
        # GPS 데이터 반환: 원본 구조(deviceId가 키인 형태) 그대로 반환
        elif self.path == "/gps":
            if os.path.exists(GPS_FILE):
                with open(GPS_FILE, "r", encoding="utf-8") as f:
                    # 가공 로직을 삭제하고 파일 내용을 직접 읽어 전송합니다.
                    gps_data = f.read() 
            else:
                gps_data = "{}"
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(gps_data.encode('utf-8'))
            return

        # 호출 목록 반환
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
            self.send_response(400)
            self.end_headers()
            return

        # 1. 위치 저장 (deviceId 기준 덮어쓰기)
        if self.path == "/gps":
            device_id = data.get("deviceId")
            driver_name = data.get("id")
            lat = data.get("lat")
            lng = data.get("lng")
            if not device_id or not driver_name or lat is None or lng is None:
                self.send_response(400); self.end_headers(); return

            gps_dict = {}
            if os.path.exists(GPS_FILE):
                with open(GPS_FILE, "r", encoding="utf-8") as f:
                    try: gps_dict = json.load(f)
                    except: pass
            
            gps_dict[device_id] = {"id": driver_name, "lat": lat, "lng": lng}
            with open(GPS_FILE, "w", encoding="utf-8") as f:
                json.dump(gps_dict, f, ensure_ascii=False)

            self.send_response(200); self.end_headers()
            self.wfile.write(b"OK")

        # 2.  호출 저장 (에러 났던 부분)
        elif self.path == "/request":
            from_addr = data.get("from")
            to_addr = data.get("to")
            phone = data.get("phone")
            
            req_list = []
            if os.path.exists(REQUESTS_FILE):
                with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
                    try: req_list = json.load(f)
                    except: pass

            req_list.append({"from": from_addr, "to": to_addr, "phone": phone})
            with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
                json.dump(req_list, f, ensure_ascii=False)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(" 호출이 완료되었습니다.".encode('utf-8'))

        # 3. 호출 완료 처리
        elif self.path == "/done":
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
    # 포트 8000번으로 실행
    server = HTTPServer(("0.0.0.0", 8000), MyHandler)
    print("Server started at http://localhost:8000")
    server.serve_forever()
