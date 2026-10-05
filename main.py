"""Version 1 CLI for the Electric Vehicle Charging Station Locator.

The program uses the ArcGIS Alternative Fueling Stations Feature Service
as its live data source. If the live service cannot be reached, it falls
back to the included local JSON dataset so the workflow can still be tested.
"""

import json
import math
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


DATA_FILE = Path(__file__).parent / "data" / "sample_stations.json"
ARCGIS_QUERY_URL = (
    "https://services.arcgis.com/xOi1kZaI0eWDREZv/ArcGIS/rest/services/"
    "Alternative_Fueling_Stations/FeatureServer/0/query"
)


# These are the ArcGIS fields used by Version 1.
ARCGIS_FIELDS = ",".join(
    [
        "id",
        "station_name",
        "latitude",
        "longitude",
        "city",
        "state",
        "street_address",
        "zip",
        "ev_connector_types",
        "ev_dc_fast_num",
        "ev_level1_evse_num",
        "ev_level2_evse_num",
        "ev_network",
        "ev_pricing",
        "access_days_time",
        "status_code",
        "access_code",
        "ev_charging_units",
    ]
)


def load_sample_stations():
    """Load local sample data used when live ArcGIS data is unavailable."""
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_distance_miles(lat1, lon1, lat2, lon2):
    """Calculate approximate straight-line distance using the Haversine formula."""
    earth_radius_miles = 3958.8

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius_miles * c


def fetch_arcgis_stations(latitude, longitude, max_results=100):
    """Request nearby electric stations from the ArcGIS Feature Service."""
    params = {
        "where": "fuel_type_code='ELEC'",
        "outFields": ARCGIS_FIELDS,
        "returnGeometry": "false",
        "geometry": f"{longitude},{latitude}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "distance": 25,
        "units": "esriSRUnit_StatuteMile",
        "resultRecordCount": max_results,
        "f": "json",
    }

    url = f"{ARCGIS_QUERY_URL}?{urlencode(params)}"
    request = Request(
        url,
        headers={"User-Agent": "EV-Charging-Locator-HCI5840/1.0"},
    )

    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_power_kw(charging_units):
    """Try to find a numeric charging power value in ArcGIS charging-unit data."""
    if not charging_units:
        return None

    if isinstance(charging_units, str):
        try:
            charging_units = json.loads(charging_units)
        except json.JSONDecodeError:
            return None

    powers = []

    def search(value):
        if isinstance(value, dict):
            for key, item in value.items():
                normalized_key = str(key).lower().replace("_", "")
                if normalized_key in {"powerkw", "powerkilowatts"}:
                    if isinstance(item, (int, float)):
                        powers.append(float(item))
                    else:
                        try:
                            powers.append(float(item))
                        except (TypeError, ValueError):
                            pass
                else:
                    search(item)
        elif isinstance(value, list):
            for item in value:
                search(item)

    search(charging_units)
    return max(powers) if powers else None


def parse_price_per_kwh(pricing_text):
    """Extract a simple dollar-per-kWh value when the source provides one."""
    if not pricing_text:
        return None

    text = str(pricing_text)
    lower_text = text.lower()
    marker = "/kwh"

    if marker not in lower_text:
        return None

    before_kwh = lower_text.split(marker, 1)[0]
    digits = []
    current = ""

    for character in reversed(before_kwh):
        if character.isdigit() or character == ".":
            current = character + current
        elif current:
            break

    if current:
        try:
            return float(current)
        except ValueError:
            return None

    return None


def map_status(status_code):
    """Convert the ArcGIS status code into a user-friendly label."""
    status_map = {
        "E": "Available",
        "T": "Temporarily unavailable",
        "P": "Planned",
    }
    return status_map.get(str(status_code).upper(), "Unknown")


def normalize_arcgis_station(raw_station, user_latitude, user_longitude):
    """Convert an ArcGIS record into the simpler station structure used by the app."""
    station_lat = raw_station.get("latitude")
    station_lon = raw_station.get("longitude")

    distance = None
    if station_lat is not None and station_lon is not None:
        distance = calculate_distance_miles(
            user_latitude,
            user_longitude,
            station_lat,
            station_lon,
        )

    connector = raw_station.get("ev_connector_types") or "Unknown"
    power_kw = parse_power_kw(raw_station.get("ev_charging_units"))
    price = parse_price_per_kwh(raw_station.get("ev_pricing"))

    total_chargers = sum(
        value or 0
        for value in [
            raw_station.get("ev_dc_fast_num"),
            raw_station.get("ev_level1_evse_num"),
            raw_station.get("ev_level2_evse_num"),
        ]
        if isinstance(value, (int, float))
    )

    chargers = total_chargers if total_chargers else "Unknown"
    address = raw_station.get("street_address") or "Address unavailable"
    zip_code = raw_station.get("zip") or ""
    if zip_code:
        address = f"{address}, {zip_code}"

    access_code = str(raw_station.get("access_code") or "").lower()
    if access_code and access_code != "public":
        availability = "Restricted/private"
    else:
        availability = map_status(raw_station.get("status_code"))

    return {
        "id": raw_station.get("id"),
        "name": raw_station.get("station_name") or "Unnamed Station",
        "address": address,
        "city": raw_station.get("city") or "",
        "state": raw_station.get("state") or "",
        "latitude": station_lat,
        "longitude": station_lon,
        "distance_miles": distance,
        "connector": connector,
        "power_kw": power_kw,
        "price_per_kwh": price,
        "availability": availability,
        "operator": raw_station.get("ev_network") or "Unknown",
        "status": map_status(raw_station.get("status_code")),
        "chargers": chargers,
        "hours": raw_station.get("access_days_time") or "Unknown",
        "pricing_details": raw_station.get("ev_pricing") or "Unknown",
    }


def get_charging_stations(latitude, longitude):
    """Get live ArcGIS data; otherwise return local test data."""
    try:
        response = fetch_arcgis_stations(latitude, longitude)
        raw_stations = response.get("features", [])
        stations = [
            normalize_arcgis_station(
                feature.get("attributes", {}),
                latitude,
                longitude,
            )
            for feature in raw_stations
        ]
        stations = [s for s in stations if s["distance_miles"] is not None]
        return stations, "ArcGIS Alternative Fueling Stations"
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as error:
        print(f"\nLive ArcGIS request failed: {error}")
        print("Falling back to the local sample dataset.\n")

    stations = load_sample_stations()
    return stations, "local sample data"


def filter_stations(stations, max_distance=None, connector=None,
                    min_power=None, max_price=None, available_only=False):
    """Apply the user's search filters to station records."""
    filtered = []

    for station in stations:
        distance = station.get("distance_miles")
        power = station.get("power_kw")
        price = station.get("price_per_kwh")
        station_connector = str(station.get("connector", "")).lower()
        availability = str(station.get("availability", "")).lower()

        if max_distance is not None and (distance is None or distance > max_distance):
            continue
        if connector and connector.lower() not in station_connector:
            continue
        if min_power is not None and (power is None or power < min_power):
            continue
        if max_price is not None and (price is None or price > max_price):
            continue
        if available_only and availability != "available":
            continue

        filtered.append(station)

    return sorted(
        filtered,
        key=lambda station: station.get("distance_miles")
        if station.get("distance_miles") is not None
        else float("inf"),
    )


def display_stations(stations):
    """Display a compact numbered list of matching stations."""
    if not stations:
        print("\nNo stations matched those filters.")
        return

    print("\nMatching charging stations:")
    print("-" * 72)

    for index, station in enumerate(stations, start=1):
        distance = station.get("distance_miles")
        distance_text = f"{distance:.1f} mi" if distance is not None else "distance unknown"
        power = station.get("power_kw")
        power_text = f"{power:g} kW" if isinstance(power, (int, float)) else "power unknown"
        price = station.get("price_per_kwh")
        price_text = f"${price:.2f}/kWh" if isinstance(price, (int, float)) else "price unknown"

        print(
            f"{index}. {station['name']} | {distance_text} | "
            f"{station['connector']} | {power_text} | {price_text} | "
            f"{station['availability']}"
        )

    print("-" * 72)


def display_station_details(station):
    """Display useful Version 1 details for one station."""
    print("\nStation Details")
    print("=" * 40)
    print(f"Name:        {station.get('name', 'Unknown')}")
    print(f"Address:     {station.get('address', 'Unknown')}")
    print(f"City/State:  {station.get('city', '')}, {station.get('state', '')}")
    print(f"Distance:    {format_distance(station.get('distance_miles'))}")
    print(f"Connector:   {station.get('connector', 'Unknown')}")
    print(f"Power:       {format_power(station.get('power_kw'))}")
    print(f"Price:       {format_price(station.get('price_per_kwh'))}")
    print(f"Availability:{station.get('availability', 'Unknown')}")
    print(f"Operator:    {station.get('operator', 'Unknown')}")
    print(f"Chargers:    {station.get('chargers', 'Unknown')}")
    print(f"Hours:       {station.get('hours', 'Unknown')}")
    print(f"Pricing info:{station.get('pricing_details', 'Unknown')}")


def format_distance(value):
    return f"{value:.1f} miles" if isinstance(value, (int, float)) else "Unknown"


def format_power(value):
    return f"{value:g} kW" if isinstance(value, (int, float)) else "Unknown"


def format_price(value):
    return f"${value:.2f}/kWh" if isinstance(value, (int, float)) else "Unknown"


def get_float(prompt, allow_blank=True, minimum=0):
    """Safely read an optional number from the CLI."""
    while True:
        value = input(prompt).strip()
        if allow_blank and value == "":
            return None
        try:
            number = float(value)
            if number < minimum:
                print(f"Please enter a number >= {minimum}.")
                continue
            return number
        except ValueError:
            print("Please enter a valid number.")


def get_location():
    """Read latitude and longitude from the user."""
    print("\nEnter the search location.")
    latitude = get_float("Latitude: ", allow_blank=False, minimum=-90)
    longitude = get_float("Longitude: ", allow_blank=False, minimum=-180)
    return latitude, longitude


def get_filters():
    """Collect optional search filters from the user."""
    print("\nOptional filters — press Enter to skip a filter.")
    max_distance = get_float("Maximum distance in miles: ")
    connector = input("Connector type (e.g. CCS, NACS, J1772): ").strip() or None
    min_power = get_float("Minimum charging speed in kW: ")
    max_price = get_float("Maximum price per kWh: ")
    available_answer = input("Available stations only? (y/n): ").strip().lower()
    available_only = available_answer in {"y", "yes"}

    return {
        "max_distance": max_distance,
        "connector": connector,
        "min_power": min_power,
        "max_price": max_price,
        "available_only": available_only,
    }


def choose_station(stations):
    """Let the user select one station from the displayed results."""
    if not stations:
        return None

    while True:
        choice = input(
            "\nEnter a station number for details, or press Enter to search again: "
        ).strip()
        if choice == "":
            return None
        try:
            index = int(choice) - 1
            if 0 <= index < len(stations):
                return stations[index]
            print("Please choose one of the listed station numbers.")
        except ValueError:
            print("Please enter a station number.")


def run_search():
    """Run one complete search from location input through station details."""
    latitude, longitude = get_location()
    stations, source = get_charging_stations(latitude, longitude)

    print(f"\nStation data source: {source}")
    print(f"Stations loaded: {len(stations)}")

    if source == "local sample data":
        print("Note: sample distances are fixed test values.")

    filters = get_filters()
    matches = filter_stations(stations, **filters)
    display_stations(matches)

    selected_station = choose_station(matches)
    if selected_station:
        display_station_details(selected_station)


def main():
    """Run the menu-driven Version 1 CLI."""
    print("EV CHARGING STATION LOCATOR — VERSION 1")
    print("Find and filter nearby EV charging stations.\n")

    while True:
        print("\n1. Search for charging stations")
        print("2. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            try:
                run_search()
            except KeyboardInterrupt:
                print("\nSearch cancelled.")
            except Exception as error:
                print(f"\nUnexpected error: {error}")
                print("See bugs.md if this problem needs to be tracked.")
        elif choice == "2":
            print("Goodbye!")
            break
        else:
            print("Please enter 1 or 2.")


if __name__ == "__main__":
    main()
