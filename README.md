# DParker_Project
the project is an electric vehicle (EV) Charging Station Locatr deskigned to help electric vehicle drivers quickly find charging stations. The applicationn woiuld display on an interactive map and provide information such as distance, connector type, charging speed, cost, and availability. Users could filter stations based on their needs.

# EV Charging Station Locator — Version 1

This Python command-line app helps EV drivers find nearby charging stations and filter them by distance, connector type, charging speed, price, and availability.

## Version 1

Version 1 focuses on the project's core data flow rather than a graphical interface:

1. Enter a latitude and longitude.
2. Query the ArcGIS Alternative Fueling Stations Feature Service for nearby electric charging stations.
3. Convert the ArcGIS records into the simpler station format used by the program.
4. Filter the stations by distance, connector, charging speed, price, and availability.
5. View a ranked list of matching stations.
6. Select a station to view more details.
7. Repeat the search or exit.

The eventual version could use a web/mobile-style interface with an interactive map, but the current version is intentionally CLI-based as required by the project specification.

## Files

- `main.py` — main program and all Version 1 functions.
- `bugs.md` — bug/issue tracking notes.
- `.gitignore` — Python/Git ignore rules, including `keys.py` in case credentials are needed for a future service.
- `LICENSE` — MIT license.
- `docs/` — project sketch and project specification PDFs.
- `data/sample_stations.json` — small local dataset used as a fallback for testing.

# EV Charging Station Locator — Version 1

This Python command-line app helps EV drivers find nearby charging stations and filter them by distance, connector type, charging speed, price, and availability.

## Version 2

Version 2 focuses on the project's core data flow rather than a graphical interface:

1. Enter a latitude and longitude.
2. Query the ArcGIS Alternative Fueling Stations Feature Service for nearby electric charging stations.
3. Convert the ArcGIS records into the simpler station format used by the program.
4. Filter the stations by distance, connector, charging speed, price, and availability.
5. View a ranked list of matching stations.
6. Select a station to view more details.
7. Repeat the search or exit.

The eventual version could use a web/mobile-style interface with an interactive map, but the current version is intentionally CLI-based as required by the project specification.

## Data source

Version 1 uses the ArcGIS **Alternative Fueling Stations** Feature Service provided by ArcGIS. The service describes the dataset as an alternative-fueling-station dataset updated daily from the National Laboratory of the Rockies (NLR) and includes station locations, EV connector information, EV charging counts, network, pricing, access, and status fields.

ArcGIS service:

`https://services.arcgis.com/xOi1kZaI0eWDREZv/ArcGIS/rest/services/Alternative_Fueling_Stations/FeatureServer/0`

The program sends a JSON query for records where `fuel_type_code='ELEC'` within 25 miles of the latitude/longitude entered by the user.

No API key is required for this public ArcGIS query.

## Local fallback data

The project also includes `data/sample_stations.json`. If the ArcGIS service is unavailable, the program automatically falls back to this small local dataset so the complete CLI workflow can still be tested.

## Files

- `main.py` — main program and all Version 1 functions.
- `bugs.md` — bug/issue tracking notes.
- `.gitignore` — Python/Git ignore rules, including `keys.py` in case credentials are needed for a future service.
- `LICENSE` — MIT license.
- `docs/` — project sketch and project specification PDFs.
- `data/sample_stations.json` — small local dataset used as a fallback for testing.

## Run

From the project root:

```bash
python main.py
```

No API key is required for the ArcGIS data source or for the included sample-data fallback.


## Installation

Version 2 uses the `requests` library for the ArcGIS web request. From the project folder, install the dependency with:

```bash
python3 -m pip install -r requirements.txt
```

Then run:

```bash
python3 main.py
```

The program keeps SSL certificate verification enabled. If the live ArcGIS request fails, it falls back to the local sample dataset and reports the failure.
