let map;
let marker;

function initMap() {
  const defaultLocation = { lat: 51.5, lng: -0.12 };

  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 6,
    center: defaultLocation,
    streetViewControl: false,
    zoomControl: true,
    rotateControl: false,
    styles: [/* your existing styles */]
  });

  map.addListener("click", function (event) {
    const lat = event.latLng.lat();
    const lng = event.latLng.lng();

    console.log("🗺️ Map clicked at:", lat, lng);
    

    // ✅ Remove old marker
    if (marker) marker.setMap(null);

    // ✅ Add new marker
    marker = new google.maps.Marker({
      position: { lat, lng },
      map: map,
      title: "Selected Location"
    });

    
    // ✅ Update Alpine global store
    Alpine.store('app').location = { lat: lat, lng: lng };

    console.log('?????!!!');

    console.log('####');
    console.log(Alpine.store('app'));
    console.log('####');

  });
}

window.initMap = initMap;