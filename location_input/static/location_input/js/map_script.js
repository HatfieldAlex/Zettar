import { mapOptions, geojsonGeometryToGMapPaths } from './map_config.js';

let map;
let marker;


async function initMap() {
  map = new google.maps.Map(document.getElementById("map"), mapOptions);

  try {
    const resp = await fetch('/static/location_input/data/dno_licence_areas.geojson'); // host locally or via your CDN
    const geojson = await resp.json();
    const AvailableRegions = geojson.features.filter(f => f.properties?.dno === "NGED");
    const allAvailablePaths = AvailableRegions.flatMap(r => geojsonGeometryToGMapPaths(r.geometry));

    const UnavailableRegions = geojson.features.filter(f => f.properties?.dno !== "NGED");
    const allUnavailablePaths = UnavailableRegions.flatMap(r => geojsonGeometryToGMapPaths(r.geometry));


    AvailableRegions.forEach(r => {
        const poly = new google.maps.Polygon({
        paths: allAvailablePaths,
        strokeOpacity: 0,         // no border
        fillColor: "#5bc4a1ff",     // warm, eye-catching fill
        fillOpacity: 0,        // see the map details underneath
        clickable: true,
        zIndex: 2
        });
        poly.setMap(map);
        poly.addListener("click", onMapClick);
    });

    UnavailableRegions.forEach(r => {
        const poly = new google.maps.Polygon({
        paths: allUnavailablePaths,
        strokeOpacity: 0,         // no border
        fillColor: "#e88b82ff",     // warm, eye-catching fill
        fillOpacity: 0.10,        // see the map details underneath
        clickable: true,
        zIndex: 2
        });
        poly.setMap(map);
        poly.addListener("click", onMapClick);
    });

  } catch (e) {
    console.error("Error occured when finding map rendering", e);
  }

  map.addListener("click", onMapClick);
}

function onMapClick(event) {
  // Works for both polygon clicks and base map clicks
  const lat = event.latLng.lat();
  const lng = event.latLng.lng();
  console.log("Map clicked at:", lat, lng);

  if (marker) marker.setMap(null);
  
  marker = new google.maps.Marker({
    position: { lat, lng },
    map: map,
    title: "Selected Location",
  });

  // Update Alpine global store
  Alpine.store('app').location = { lat, lng };
}



window.initMap = initMap;

