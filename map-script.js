let map;
let markers = {};
let infowindow;

function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 17, //기존 14 → 16으로 상승 해서 4배더 확대 함.
    center: {lat: 35.7384, lng: 128.7334}
  });

  infowindow = new google.maps.InfoWindow();

  loadGPS();
  setInterval(loadGPS, 3000);
}

function getOffset(index) {
  const offset = 0.00005;
  return (index % 5) * offset;
}

function loadGPS() {
  if (!map) {
    console.warn("Map is not initialized yet");
    return;
  }

  fetch('/gps')
    .then(r => r.json())
    .then(data => {
      let i = 0;
      for (let id in data) {
        let baseLat = data[id].lat;
        let baseLng = data[id].lng;

        let pos = {
          lat: baseLat + getOffset(i),
          lng: baseLng + getOffset(i + 2)
        };

        let color = "#ff3b3b";

        if (!markers[id]) {
          let marker = new google.maps.Marker({
            position: pos,
            map: map,
            label: {
              text: id.substring(0, 1),
              color: color,
            },
            icon: {
              path: google.maps.SymbolPath.CIRCLE,
              scale: 10,
              fillColor: color,
              fillOpacity: 1,
              strokeColor: "black",
              strokeWeight: 2,
            }
          });

          marker.addListener('click', () => {
            infowindow.setContent(id + " 위치");
            infowindow.open(map, marker);
          });

          markers[id] = marker;
        } else {
          markers[id].setPosition(pos);
        }

        i++;
      }
    })
    .catch(e => console.error("GPS load error:", e));
}