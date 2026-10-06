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
