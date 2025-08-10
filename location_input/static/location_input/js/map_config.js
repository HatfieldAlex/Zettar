export const mapOptions = {
  zoom: 8,
  center: { lat: 51.70, lng: -2.35 },
  streetViewControl: false,
  zoomControl: true,
  rotateControl: false,
  styles: [/* your existing styles */],
};


export function geojsonGeometryToGMapPaths(geom) {
  const rings = geom.type === 'Polygon'
    ? geom.coordinates
    : geom.coordinates.flat(); 
  return rings.map(ring => ring.map(([lng, lat]) => ({ lat, lng })));
}

