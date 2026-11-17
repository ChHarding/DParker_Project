"""Version 1 CLI for the Electric Vehicle Charging Station Locator.

The program uses the ArcGIS Alternative Fueling Stations Feature Service
as its live data source. If the live service cannot be reached, it falls
back to the included local JSON dataset so the workflow can still be tested.
"""

import json
import math
from pathlib import Path
import requests
import ast


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
    """Request nearby electric stations from the ArcGIS Feature Service.

    Args:
        latitude: Search latitude in decimal degrees.
        longitude: Search longitude in decimal degrees.
        max_results: Maximum number of records to request.

    Returns:
        The decoded JSON response from ArcGIS.

    Raises:
        requests.RequestException: If the HTTP request fails.
        ValueError: If ArcGIS returns an error in an otherwise valid response.
    """
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

    response = requests.get(
        ARCGIS_QUERY_URL,
        params=params,
        headers={"User-Agent": "EV-Charging-Locator-HCI5840/2.0"},
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()
    if "error" in data:
        error = data["error"]
        message = error.get("message", "Unknown ArcGIS service error.")
        details = "; ".join(error.get("details", []))
        if details:
            message = f"{message} {details}"
        raise ValueError(message)

    return data



def parse_power_kw(charging_units):
    """Extract the highest available charging power in kilowatts."""
    if not charging_units:
        return None

    # ArcGIS may return this field as a Python-style string
    # rather than valid JSON.
    if isinstance(charging_units, str):
        try:
            charging_units = json.loads(charging_units)
        except json.JSONDecodeError:
            try:
                charging_units = ast.literal_eval(charging_units)
            except (ValueError, SyntaxError):
                return None

    power_values = []

    def find_power(data):
        """Recursively find power_kw values in nested data."""
        if isinstance(data, dict):
            for key, value in data.items():
                normalized_key = key.lower().replace("_", "")

                if normalized_key in ("powerkw", "powerkilowatts"):
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        power_values.append(value)
                else:
                    find_power(value)

        elif isinstance(data, list):
            for item in data:
                find_power(item)

    find_power(charging_units)

    return max(power_values) if power_values else None


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
    except (requests.RequestException, ValueError, json.JSONDecodeError, OSError) as error:
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


def format_distance(value):
    """Format a distance value for display."""
    return f"{value:.1f} miles" if isinstance(value, (int, float)) else "Unknown"


def format_power(value):
    """Format charging power for display."""
    return f"{value:g} kW" if isinstance(value, (int, float)) else "Unknown"


def format_price(value):
    """Format charging price for display."""
    return f"${value:.2f}/kWh" if isinstance(value, (int, float)) else "Unknown"


def main():
    """Run the Streamlit EV charging station locator."""
    import streamlit as st
    from geocoding import geocode_address

    st.set_page_config(
        page_title="EV Charging Station Locator",
        page_icon="🔌",
        layout="wide",
    )

    st.title("🔌 EV Charging Station Locator")
    st.write(
        "Find electric vehicle charging stations near an address, "
        "city, or landmark."
    )

    st.subheader("Where are you looking for charging stations?")

    with st.form("search_form"):
        address = st.text_input(
            "Enter an address or location",
            placeholder="Example: Iowa State University, Ames, IA",
        )
        search_button = st.form_submit_button("Find Charging Stations")

    st.sidebar.header("Search Filters")

    max_distance = st.sidebar.number_input(
        "Maximum distance (miles)",
        min_value=1.0,
        max_value=25.0,
        value=25.0,
    )

    connector_options = {
        "Any": None,
        "CCS": "J1772COMBO",
        "NACS": "TESTLA",
        "J1772": "J1772",
        "CHAdeMO": "CHADEMO",
    }

    connector = st.sidebar.selectbox(
        "Connector type",
        list(connector_options.keys()),
    )

    min_power = st.sidebar.number_input(
        "Minimum charging speed (kW)",
        min_value=0.0,
        value=0.0,
        step=5.0,
    )

    max_price = st.sidebar.number_input(
        "Maximum price ($/kWh)",
        min_value=0.0,
        value=0.0,
        step=0.05,
        help="Enter 0 to ignore this filter.",
    )

    available_only = st.sidebar.checkbox(
        "Show available stations only"
    )

    if search_button:
        if not address.strip():
            st.error("Please enter an address or location.")
            return

        with st.spinner("Finding your location..."):
            try:
                coordinates = geocode_address(address.strip())

                if coordinates is None:
                    st.error(
                        "We couldn't find that location. "
                        "Try entering a more specific address."
                    )
                    return

            except requests.RequestException as error:
                st.error(f"Location search failed: {error}")
                return

        latitude, longitude = coordinates

        st.success(
            f"Location found! Coordinates: "
            f"{latitude:.5f}, {longitude:.5f}"
        )

        with st.spinner("Searching for nearby charging stations..."):
            try:
                stations, source = get_charging_stations(
                    latitude,
                    longitude,
                )
            except Exception as error:
                st.error(f"Unable to retrieve charging stations: {error}")
                return

        st.caption(f"Data source: {source}")

        if source == "local sample data":
            st.warning(
                "Live station data is unavailable. "
                "Showing local sample data instead."
            )

        filters = {
            "max_distance": max_distance,
            "connector": connector_options[connector],
            "min_power": min_power if min_power > 0 else None,
            "max_price": max_price if max_price > 0 else None,
            "available_only": available_only,
        }

        matches = filter_stations(stations, **filters)

        st.subheader("Charging Station Results")

        col1, col2 = st.columns(2)
        col1.metric("Stations found", len(matches))
        col2.metric("Stations within search area", len(stations))

        if not matches:
            st.info(
                "No stations matched your filters. "
                "Try increasing the distance or changing your filters."
            )
            return

        map_data = [
            {
                "latitude": station["latitude"],
                "longitude": station["longitude"],
            }
            for station in matches
            if station.get("latitude") is not None
            and station.get("longitude") is not None
        ]

        if map_data:
            st.subheader("Station Map")
            st.map(map_data, latitude="latitude", longitude="longitude")

        for index, station in enumerate(matches, start=1):
            with st.expander(
                f"{index}. {station['name']} — "
                f"{format_distance(station.get('distance_miles'))}"
            ):
                st.write(f"**Address:** {station.get('address', 'Unknown')}")
                st.write(
                    f"**City/State:** "
                    f"{station.get('city', '')}, {station.get('state', '')}"
                )
                st.write(
                    f"**Connector:** {station.get('connector', 'Unknown')}"
                )
                st.write(
                    f"**Charging speed:** "
                    f"{format_power(station.get('power_kw'))}"
                )
                st.write(
                    f"**Price:** "
                    f"{format_price(station.get('price_per_kwh'))}"
                )
                st.write(
                    f"**Availability:** "
                    f"{station.get('availability', 'Unknown')}"
                )
                st.write(
                    f"**Network/operator:** "
                    f"{station.get('operator', 'Unknown')}"
                )
                st.write(
                    f"**Number of chargers:** "
                    f"{station.get('chargers', 'Unknown')}"
                )
                st.write(f"**Hours:** {station.get('hours', 'Unknown')}")
                st.write(
                    f"**Pricing information:** "
                    f"{station.get('pricing_details', 'Unknown')}"
                )


if __name__ == "__main__":
    main()
