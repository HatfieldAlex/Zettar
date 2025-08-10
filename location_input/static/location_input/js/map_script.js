import { mapOptions, geojsonGeometryToGMapPaths, UnavailableRegionOptions, AvailableRegionOptions } from './map_config.js';

let map;
let marker;

function onMapClick(event) {
  const lat = event.latLng.lat();
  const lng = event.latLng.lng();
  console.log("Map clicked at:", lat, lng);

  if (marker) marker.setMap(null);
  
  marker = new google.maps.Marker({
    position: { lat, lng },
    map: map,
    title: "Selected Location",
  });
  Alpine.store('app').location = { lat, lng };
}


async function initMap() {
  map = new google.maps.Map(document.getElementById("map"), mapOptions);

  try {
    const resp = await fetch('/static/location_input/data/dno_licence_areas.geojson'); 
    const geojson = await resp.json();
    const AvailableRegions = geojson.features.filter(f => f.properties?.dno === "NGED");
    const allAvailablePaths = AvailableRegions.flatMap(r => geojsonGeometryToGMapPaths(r.geometry));

    const UnavailableRegions = geojson.features.filter(f => f.properties?.dno !== "NGED");
    const allUnavailablePaths = UnavailableRegions.flatMap(r => geojsonGeometryToGMapPaths(r.geometry));


    AvailableRegions.forEach(r => {
        const poly = new google.maps.Polygon({
        paths: allAvailablePaths,
        ...AvailableRegionOptions
        
        });
        poly.setMap(map);
        poly.addListener("click", onMapClick);
    });

    UnavailableRegions.forEach(r => {
        const poly = new google.maps.Polygon({
        paths: allUnavailablePaths,
        ...UnavailableRegionOptions
        });
        poly.setMap(map);
    });


  } catch (e) {
    console.error(
        `Failed to load or render map regions from /static/location_input/data/dno_licence_areas.geojson. 
        Check that the file exists, is valid GeoJSON, and the server is serving it correctly.`, 
   e);
  }
}

window.initMap = initMap;

