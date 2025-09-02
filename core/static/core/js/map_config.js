export const mapOptions = {
  zoom: 8,
  center: { lat: 51.70, lng: -2.35 },
  streetViewControl: false,
  zoomControl: true,
  rotateControl: false,
};


export function geojsonGeometryToGMapPaths(geom) {
  const rings = geom.type === 'Polygon'
    ? geom.coordinates
    : geom.coordinates.flat(); 
  return rings.map(ring => ring.map(([lng, lat]) => ({ lat, lng })));
}

export function onMapClick(event) {
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

export const UnavailableRegionOptions = {
  strokeOpacity: 0,        
  fillColor: "#d2c5c3ff",     
  fillOpacity: 0.10,        
  clickable: false,
  zIndex: 2
}

export const AvailableRegionOptions = {
        strokeOpacity: 0,         
        fillColor: "#5bc4a1ff",    
        fillOpacity: 0,       
        clickable: true,
        zIndex: 2
}