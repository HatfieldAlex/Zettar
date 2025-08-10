import { mapOptions } from './map_config.js';

let map;
let marker;

async function initMap() {
  map = new google.maps.Map(document.getElementById("map"), mapOptions);


  outlinePoly.setMap(map);
  
  outlinePoly.addListener("click", function (event) {
    const lat = event.latLng.lat();
    const lng = event.latLng.lng();
    console.log("Map clicked at:", lat, lng);

    if (marker) marker.setMap(null);
    marker = new google.maps.Marker({
      position: { lat, lng },
      map: map,
      title: "Selected Location"
    });

    // Update Alpine global store
    Alpine.store('app').location = { lat: lat, lng: lng };
  });
}

window.initMap = initMap;