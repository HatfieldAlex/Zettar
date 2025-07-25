let map;
let marker;

function initMap() {
    const defaultLocation = { lat: 51.5, lng: -0.12 };

    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 6,
        center: defaultLocation,
        styles: [
            { elementType: "geometry", stylers: [{ color: "#f5f5f5" }] },
            { elementType: "labels.icon", stylers: [{ visibility: "off" }] },
            { elementType: "labels.text.fill", stylers: [{ color: "#616161" }] },
            { elementType: "labels.text.stroke", stylers: [{ color: "#f5f5f5" }] },
            {
                featureType: "administrative.land_parcel",
                elementType: "labels.text.fill",
                stylers: [{ color: "#bdbdbd" }]
            },
            {
                featureType: "poi",
                elementType: "geometry",
                stylers: [{ color: "#eeeeee" }]
            },
            {
                featureType: "poi",
                elementType: "labels.text.fill",
                stylers: [{ color: "#757575" }]
            },
            {
                featureType: "road",
                elementType: "geometry",
                stylers: [{ color: "#ffffff" }]
            },
            {
                featureType: "road.arterial",
                elementType: "labels.text.fill",
                stylers: [{ color: "#757575" }]
            },
            {
                featureType: "road.highway",
                elementType: "geometry",
                stylers: [{ color: "#dadada" }]
            },
            {
                featureType: "transit.line",
                elementType: "geometry",
                stylers: [{ color: "#e5e5e5" }]
            },
            {
                featureType: "water",
                elementType: "geometry",
                stylers: [{ color: "#c9c9c9" }]
            },
            {
                featureType: "water",
                elementType: "labels.text.fill",
                stylers: [{ color: "#9e9e9e" }]
            }
        ]
    });

    map.addListener("click", function (event) {
        const lat = event.latLng.lat();
        const lng = event.latLng.lng();

        document.getElementById("latitude").value = lat;
        document.getElementById("longitude").value = lng;

        if (marker) marker.setMap(null);

        marker = new google.maps.Marker({
            position: { lat, lng },
            map: map
        });
    });
}

window.initMap = initMap;
