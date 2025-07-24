import requests

def get_osrm_driving_distance(coord1, coord2):
    """
    Returns the driving distance in meters between two (longitude, latitude) tuples
    using OSRM's public API.

    Parameters:
    - coord1: (lon1, lat1) tuple
    - coord2: (lon2, lat2) tuple

    Returns:
    - distance in meters (float), or None if there's an error
    """
    lon1, lat1 = coord1
    lon2, lat2 = coord2

    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and data.get("code") == "Ok":
            # Distance is in meters
            return data["routes"][0]["distance"]
        else:
            print("Error from OSRM:", data.get("message", "Unknown error"))
            return None
    except Exception as e:
        print("Request failed:", e)
        return None
