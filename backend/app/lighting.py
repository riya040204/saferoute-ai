import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def _check_point(lon, lat, radius_meters):
    """Check lighting status for a single point. Returns 'lit', 'unlit', or 'unknown'."""
    query = f"""
    [out:json][timeout:8];
    way(around:{radius_meters},{lat},{lon})["highway"];
    out tags;
    """
    try:
        response = requests.post(OVERPASS_URL, data={"data": query}, timeout=10)
        response.raise_for_status()
        data = response.json()

        for element in data.get("elements", []):
            lit = element.get("tags", {}).get("lit")
            if lit == "yes":
                return "lit"
            elif lit == "no":
                return "unlit"

        return "unknown"
    except requests.RequestException:
        return "unknown"


def get_lighting_data(coordinates, sample_every=8, radius_meters=30, max_workers=8):
    """
    coordinates: list of [lon, lat] points from a route's geometry
    sample_every: only check every Nth point (larger = faster, less precise)
    radius_meters: search radius around each point
    max_workers: how many lighting checks to run in parallel

    Returns a dict summarizing lighting coverage along the route.
    """
    sampled_points = coordinates[::sample_every]

    if not sampled_points:
        return {"lit_percent": 0, "unlit_percent": 0, "unknown_percent": 100, "points_checked": 0}

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_check_point, lon, lat, radius_meters)
            for lon, lat in sampled_points
        ]
        for future in as_completed(futures):
            results.append(future.result())

    total = len(results)
    lit_count = results.count("lit")
    unlit_count = results.count("unlit")
    unknown_count = results.count("unknown")

    return {
        "lit_percent": round((lit_count / total) * 100, 1),
        "unlit_percent": round((unlit_count / total) * 100, 1),
        "unknown_percent": round((unknown_count / total) * 100, 1),
        "points_checked": total
    }