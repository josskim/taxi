// 기사 검색 함수
function searchDriver() {
     console.log("시작!");
  const targetName = document.getElementById("searchName").value.trim();
  if (!targetName) {
    alert("이름을 입력해주세요.");
    return;
  }

  if (typeof markers !== 'undefined' && markers[targetName]) {
    const marker = markers[targetName];
    const targetPos = marker.getPosition();
    const finalZoom = 18; // 최종 도달하고 싶은 확대 레벨

    // 1. 먼저 시야 확보를 위해 줌 아웃 (이건 즉시 해도 효과가 좋습니다)
    map.setZoom(map.getZoom() - 3);

    setTimeout(() => {
      // 2. 대상지로 부드럽게 이동
      map.panTo(targetPos);

      // 3. 이동이 끝날 때쯤(약 0.5초 뒤) 부드러운 줌인 시작
      setTimeout(() => {
        smoothZoom(map, finalZoom, map.getZoom());
        
        // 4. 정보창 표시
        infowindow.setContent("<b>" + targetName + "</b> 위치");
        infowindow.open(map, marker);
      }, 500); 

    }, 300);

  } else {
    alert("해당 데이터를 찾을 수 없습니다.");
  }
}

/**
 * 부드러운 줌 효과를 주는 헬퍼 함수
 * @param {google.maps.Map} map - 지도 객체
 * @param {number} targetZoom - 최종 목표 줌 레벨
 * @param {number} currentZoom - 현재 줌 레벨
 */
function smoothZoom(map, targetZoom, currentZoom) {
  if (currentZoom >= targetZoom) {
    return;
  } else {
    // 0.1초마다 줌을 1단계씩 높임
    google.maps.event.addListenerOnce(map, 'zoom_changed', function() {
      smoothZoom(map, targetZoom, currentZoom + 1);
    });
    setTimeout(function() {
      map.setZoom(currentZoom + 1);
    }, 100); // 100ms(0.1초) 간격으로 확대
  }
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