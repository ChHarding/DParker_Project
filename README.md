# EV Charging Station Locator

An interactive web application that helps electric vehicle (EV) drivers find nearby charging stations. Users can search by address or location, view stations on a map, and filter results based on distance, connector type, charging speed, price, and availability.

## Version 2

Version 2 upgrades the original command-line application into a web-based interface using Streamlit.

### Features

- **Address-based search:** Enter an address, city, or landmark instead of manually entering latitude and longitude.
- **Geocoding:** Converts the entered location into geographic coordinates using the OpenStreetMap Nominatim service.
- **Interactive map:** Displays nearby charging stations on a map.
- **Station filters:** Narrow results by distance, connector type, minimum charging speed, maximum price, and availability.
- **Station details:** View information about matching charging stations, including location, connector types, charging speed, and pricing when available.
- **Live data:** Retrieves station information from the ArcGIS Alternative Fueling Stations Feature Service.
- **Fallback data:** Uses a local sample dataset if the live ArcGIS service cannot be reached.

## Data Sources

### ArcGIS Alternative Fueling Stations

The application retrieves EV charging station information from the ArcGIS Alternative Fueling Stations Feature Service.

Service URL:

`https://services.arcgis.com/xOi1kZaI0eWDREZv/ArcGIS/rest/services/Alternative_Fueling_Stations/FeatureServer/0`

The application queries electric vehicle charging stations near the coordinates returned by the geocoding service.

### OpenStreetMap Nominatim

The application uses the Nominatim geocoding service to convert user-entered addresses and locations into latitude and longitude coordinates.

Service URL:

`https://nominatim.openstreetmap.org/search`

## Project Structure

- `app.py` — Main Streamlit application, data retrieval, station processing, and filtering.
- `geocoding.py` — Address-to-coordinate geocoding functionality.
- `requirements.txt` — Python dependencies.
- `bugs.md` — Bug and issue tracking notes.
- `LICENSE` — MIT license.
- `.gitignore` — Git ignore rules.
- `docs/` — Project sketch and specification PDFs.
- `data/sample_stations.json` — Local sample dataset used as a fallback.

## Installation

Clone the repository and navigate to the project directory.

Install the required dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Running the Application

From the project root, run:

```bash
python3 -m streamlit run app.py
```

Streamlit will open the application in your web browser.

Enter an address or location to search for nearby charging stations.

## Version 1

The original Version 1 application used a command-line interface and required users to enter latitude and longitude manually. It established the core data retrieval, station normalization, distance calculations, and filtering functionality.

Version 2 builds on that foundation by introducing address-based search and a graphical interface.

## Notes and Limitations

- Charging station information depends on the data available from the ArcGIS service.
- Pricing information is not available for every station, so some results may not include a cost per kWh.
- If the live ArcGIS service is unavailable, the application can use the included sample dataset.
- The application keeps SSL certificate verification enabled for web requests.

## Dependencies

- Python 3.13
- Streamlit
- Requests