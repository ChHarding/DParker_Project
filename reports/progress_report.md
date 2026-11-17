# EV Charging Station Locator — Progress Report

**Project:** HCI 5840 — Electric Vehicle Charging Station Locator  
**Report date:** October 10, 2026  
**Current version:** Version 1 — command-line interface (CLI)

## Project overview

The goal of this project is to help EV drivers find nearby charging stations without needing to search across multiple apps or websites. The first version focuses on the core data flow in Python: get a location, retrieve station data, process and filter the results, show matching stations, and let the user inspect a station's details. An interactive map or graphical interface is outside the scope of Version 1 and can be considered for a later version.

## Progress completed

- Implemented a menu-driven Python CLI in `main.py`.
- Added user input for latitude and longitude.
- Switched the primary data source from the earlier API approach to the professor-suggested ArcGIS Alternative Fueling Stations Feature Service.
- Added a JSON query for electric-fuel records (`fuel_type_code='ELEC'`) within a 25-mile search radius.
- Added data-normalization functions to convert ArcGIS attributes into the station format used by the CLI.
- Kept filters for distance, connector type, charging speed, price, and station status/availability information.
- Added station-list output and a station-details view, with an option to repeat the search or exit.
- Kept `data/sample_stations.json` as a fallback so the workflow can still be exercised when the live service is unavailable.
- Updated `README.md` to document the ArcGIS source and how to run the project.
- Updated `bugs.md` to record known limitations of the source data and live-service dependency.
- Retained the project sketch and project specification in `docs/`, along with the README, `.gitignore`, MIT license, and data folder.

## Current implementation flow

`main()` → collect location → request ArcGIS records → normalize station data → apply filters → display results → select a station → display details → search again or exit.

If the live request fails, the program attempts to load the local sample dataset instead.

## Testing and verification status

- **Python syntax:** The updated `main.py` was checked for compilation errors.
- **Data processing/filtering:** The normalization and filtering logic was exercised using representative ArcGIS-style records.
- **Live ArcGIS request:** A successful live request has **not yet been confirmed** in the development environment. The first run on a computer with internet access should verify the service response and field mappings.
- **End-to-end user test:** The full interactive workflow should be run locally, including the live-data path and the sample-data fallback.

## Current challenges and limitations

- Some stations may not include every attribute needed by the filters, especially numeric price-per-kWh or charging power. Missing values may appear as `Unknown` or cause a station not to meet a selected filter.
- The dataset's station status or access fields should not be treated as guaranteed real-time charger availability.
- The live-data path depends on internet access and the ArcGIS service remaining available.
- The location search currently expects latitude and longitude rather than a city name or ZIP code.
- The project currently displays results in the terminal; it does not yet include an interactive map or GUI.

## Next steps

1. Run `python main.py` from the project root on a computer with internet access and confirm whether live ArcGIS results are returned.
2. Verify the ArcGIS field names and the values for connectors, charging power, pricing, and station status against several real records.
3. Test the fallback by temporarily disabling internet access or otherwise simulating a request failure.
4. Test the search loop and each filter with multiple combinations, including blank filters and missing station attributes.
5. Record reproducible issues and fixes in `bugs.md` and update this report after testing.
6. Commit the changes to Git with meaningful, action-oriented commit messages.
7. Consider GUI/map work only after the Version 1 CLI and data flow are reliable.

## Overall status

**Version 1 is implemented at the code and project-structure level, with live ArcGIS integration added.** The next priority is to validate the live request and field mapping in the user's local environment, then test the complete CLI workflow and document any bugs. The project remains focused on the Version 1 CLI requirements rather than the future GUI.
