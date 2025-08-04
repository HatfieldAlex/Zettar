let map;
let marker;

import { mapOptions } from './map_config.js';


function initMap() {


  map = new google.maps.Map(document.getElementById("map"), mapOptions);

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