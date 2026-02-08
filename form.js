// 기사 검색 함수
function searchDriver() {
  const targetName = document.getElementById("searchName").value.trim();
  if (!targetName) return;

  let foundMarker = null;
  // markers 객체(deviceId 기반)를 순회하며 이름이 일치하는 마커 찾기
  for (let devId in markers) {
    if (markers[devId].getLabel().text === targetName) {
      foundMarker = markers[devId];
      break;
    }
  }

  if (foundMarker) {
    const targetPos = foundMarker.getPosition();
    map.setZoom(map.getZoom() - 3); // 줌 아웃

    setTimeout(() => {
      map.panTo(targetPos);
      setTimeout(() => {
        smoothZoom(map, 18, map.getZoom()); // 부드러운 줌 인
        infowindow.setContent("<b>" + targetName + "</b> 기사님 위치");
        infowindow.open(map, foundMarker);
      }, 600);
    }, 300);
  } else {
    alert("기사를 찾을 수 없습니다.");
  }
}

// 부드러운 줌 헬퍼 함수
function smoothZoom(map, target, current) {
  if (current >= target) return;
  google.maps.event.addListenerOnce(map, 'zoom_changed', () => {
    smoothZoom(map, target, current + 1);
  });
  setTimeout(() => { map.setZoom(current + 1); }, 100);
}



function send() {
  const from = document.getElementById("from").value.trim();
  const to = document.getElementById("to").value.trim();
  const phone = document.getElementById("phone").value.trim();

  const msg = document.getElementById("msg");
  if (!from || !to || !phone) {
    msg.style.color = "#e03e2f";
    msg.innerText = "모든 항목을 입력해주세요.";
    return;
  }

  fetch('/request', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ from, to, phone })
  })
    .then(r => r.text())
    .then(t => {
      msg.style.color = "#0078d7";
      msg.innerText = t;
      document.getElementById("from").value = "";
      document.getElementById("to").value = "";
      document.getElementById("phone").value = "";
    })
    .catch(e => {
      msg.style.color = "#e03e2f";
      msg.innerText = "서버 요청 중 오류가 발생했습니다.";
      console.error(e);
    });
}