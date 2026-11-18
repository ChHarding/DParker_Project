
"""Convert user-entered addresses into geographic coordinates."""

import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode_address(address):
    """Find the latitude and longitude for a supplied address.

    Args:
        address: Street address, city, landmark, or place name.

    Returns:
        A tuple containing (latitude, longitude), or None if no
        matching location is found.

    Raises:
        requests.RequestException: If the geocoding request fails.
    """
    params = {
        "q": address,
        "format": "jsonv2",
        "limit": 1,
    }

    response = requests.get(
        NOMINATIM_URL,
        params=params,
        headers={
            "User-Agent": "EV-Charging-Locator-HCI5840/2.0"
        },
        timeout=15,
    )
    response.raise_for_status()

    results = response.json()

    if not results:
        return None

    latitude = float(results[0]["lat"])
    longitude = float(results[0]["lon"])

    return latitude, longitude
