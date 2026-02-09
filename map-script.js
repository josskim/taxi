let map;
let markers = {}; // 현재 지도에 표시된 마커 객체들
let infowindow;

// 1. 초기 지도 설정 (비동기)
async function initMap() {
  // 기본 좌표: 경산시 부근 (제공해주신 좌표 기준)
  let initialCenter = {lat: 35.7384, lng: 128.7334}; 
  const myDeviceId = localStorage.getItem("deviceId");

  try {
    // [수정] 도메인 대신 상대 경로 /gps 사용 권장 (CORS 방지)
    const response = await fetch('/gps');
    const data = await response.json();

    // 내 기기 ID가 서버 데이터에 존재하면 해당 좌표를 중심으로 설정
    if (myDeviceId && data[myDeviceId]) {
      const myInfo = data[myDeviceId];
      initialCenter = { lat: myInfo.lat, lng: myInfo.lng };
      console.log("내 위치로 시작합니다:", myInfo.id);
    }
  } catch (e) {
    console.error("초기 데이터 로드 실패:", e);
  }

  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 17,
    center: initialCenter,
    gestureHandling: 'greedy' // [추가] 마우스 휠로 즉시 줌 가능하게 설정
  });

  infowindow = new google.maps.InfoWindow();

  // 최초 로드 및 3초마다 반복 실행
  loadGPS();
  setInterval(loadGPS, 3000);
}

// 2. 실시간 마커 업데이트 및 삭제 로직
function loadGPS() {
  if (!map) return;

  fetch('/gps') // [수정] 상대 경로 사용
    .then(r => r.json())
    .then(data => {
      // [A] 서버 데이터에 있는 기기들 처리 (추가 및 업데이트)
      for (let devId in data) {
        const info = data[devId];
        const pos = { lat: info.lat, lng: info.lng };
        const driverName = info.id;

        if (!markers[devId]) {
          // 신규 마커 생성
          let marker = new google.maps.Marker({
            position: pos,
            map: map,
            label: { text: driverName, className: "marker-label" },
            icon: {
              url: "./image/man.png",
              scaledSize: new google.maps.Size(40, 40),
              anchor: new google.maps.Point(20, 40)
            }
          });

          marker.addListener('click', () => {
            infowindow.setContent("<b>" + driverName + "</b> 기사님");
            infowindow.open(map, marker);
          });
          markers[devId] = marker;
        } else {
          // 기존 마커 위치 업데이트
          markers[devId].setPosition(pos);
          markers[devId].setLabel({text: driverName, className: "marker-label"});
        }
      }

      // [B] 중요 수정: 서버 데이터(data)에는 없는데, 내 지도(markers)에는 남아있는 마커 삭제
      for (let devId in markers) {
        if (!data[devId]) {
            // 1. 지도에서 마커 제거
            markers[devId].setMap(null);
            // 2. 메모리(객체)에서 삭제
            delete markers[devId];
            console.log(devId + " 기기가 접속을 종료하여 지도에서 제거했습니다...");
        }
      }
    })
    .catch(err => console.error("데이터 로드 에러:", err));
}
