// import { mapOptions, boundaryPath } from './map_config.js'; // keep boundaryPath as a fallback if you want
import { mapOptions, boundaryPath } from './map_config.js';

let map;
let marker;

// Convert GeoJSON geometry (Polygon | MultiPolygon) to Google Maps paths
function geojsonGeometryToGMapPaths(geom) {
  const rings = geom.type === 'Polygon'
    ? geom.coordinates
    : geom.coordinates.flat(); // flatten MultiPolygon parts into one list of rings
  return rings.map(ring => ring.map(([lng, lat]) => ({ lat, lng })));
}


async function initMap() {
  map = new google.maps.Map(document.getElementById("map"), mapOptions);

  try {
    const resp = await fetch('/static/location_input/data/dno_licence_areas.geojson'); // host locally or via your CDN
    const geojson = await resp.json();
    const WestMidlands = geojson.features.find(f => f.properties?.region === "West Midlands");


    const path = geojsonGeometryToGMapPaths(WestMidlands.geometry)

    const poly = new google.maps.Polygon({
    paths: path,
    // paths: boundaryPath,
    strokeColor: "#000000",
    strokeOpacity: 0.4,
    strokeWeight: 1,
    fillOpacity: 0,
    clickable: true,
    });

    poly.setMap(map);

    poly.addListener("click", onMapClick);


  } catch (e) {
    console.error("Failed to load NGED GeoJSON, falling back to static boundaryPath", e);

    // ---- OPTIONAL FALLBACK using your existing boundaryPath ----
    // const outlinePoly = new google.maps.Polygon({
    //   paths: boundaryPath,
    //   strokeColor: "#000000",
    //   strokeOpacity: 0.4,
    //   strokeWeight: 1,
    //   fillOpacity: 0,
    //   clickable: true,
    // });
    // outlinePoly.setMap(map);
    // outlinePoly.addListener("click", onMapClick);
    // outlinePolys = [outlinePoly];
  }

  // Also allow clicks anywhere on the base map (if you still want that)
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
