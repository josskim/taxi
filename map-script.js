let map;
let markers = {};
let infowindow;

// 1. 초기 지도 설정 (비동기)
async function initMap() {
  let initialCenter = {lat: 35.7384, lng: 128.7334}; // 기본 좌표
  const myDeviceId = localStorage.getItem("deviceId");

  try {
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
    center: initialCenter
  });

  infowindow = new google.maps.InfoWindow();

  loadGPS();
  setInterval(loadGPS, 3000);
}

// 2. 실시간 마커 업데이트
function loadGPS() {
  if (!map) return;

  fetch('/gps')
    .then(r => r.json())
    .then(data => {
      for (let devId in data) {
        const info = data[devId];
        const pos = { lat: info.lat, lng: info.lng };
        const driverName = info.id;

        if (!markers[devId]) {
          // 신규 마커 생성 (deviceId를 키로 사용)
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
          // 기존 마커 업데이트
          markers[devId].setPosition(pos);
          markers[devId].setLabel({text: driverName, className: "marker-label"});
        }
      }
    });
}
