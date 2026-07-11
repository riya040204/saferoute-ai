import requests

OSRM_BASE_URL = "https://router.project-osrm.org"

def get_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    """
    Calls the public OSRM demo server to get a route between two points.
    OSRM expects coordinates as lon,lat (note: longitude first, not latitude).
    """
    coords = f"{start_lon},{start_lat};{end_lon},{end_lat}"
    url = f"{OSRM_BASE_URL}/route/v1/driving/{coords}"

    params = {
        "overview": "full",       # return full route geometry
        "geometries": "geojson",  # geometry format easy to use on maps later
        "alternatives": "true",   # ask for alternative routes too
        "steps": "false"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()  # raises an error if the request failed
    data = response.json()

    if data["code"] != "Ok":
        raise ValueError(f"OSRM error: {data['code']}")

    routes = []
    for route in data["routes"]:
        routes.append({
            "distance_meters": route["distance"],
            "duration_seconds": route["duration"],
            "geometry": route["geometry"]  # GeoJSON LineString - list of [lon, lat] points
        })

    return routes
