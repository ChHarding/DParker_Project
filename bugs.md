# Bug and Issue Tracking

## Current Issues and Limitations

- **Missing pricing information:** The ArcGIS service does not consistently provide a numeric price-per-kWh value. In testing, none of the 47 stations returned in the Iowa State University search included pricing information. Stations with unknown pricing are excluded when a maximum-price filter is applied.
- **Missing charging power information:** Charging power is extracted from the ArcGIS charging-unit data when a numeric value is available. If power information is missing, the application displays `Unknown`, and a minimum-power filter excludes that station.
- **Availability limitations:** Real-time charger availability is not guaranteed by the station dataset. The application uses the station status and access fields provided by the data source rather than claiming a charger is currently available.
- **Internet dependency:** The live ArcGIS service and Nominatim geocoding service require an internet connection. If the ArcGIS service cannot be reached, the application falls back to the local sample dataset. Address searches still require access to the geocoding service.

## Resolved Issues — Version 2

### 1. SSL Certificate Error

- **Problem:** The original ArcGIS request using `urllib.request.urlopen()` encountered an SSL certificate verification error.
- **How to reproduce:** Run the application and attempt to retrieve live station data.
- **Expected:** The application should securely connect to the ArcGIS service.
- **Actual:** The request encountered an SSL certificate error in the original implementation.
- **Resolution:** Replaced `urllib` with the `requests` library and retained SSL certificate verification. SSL verification was not disabled.

### 2. Address Geocoding

- **Problem:** Version 1 required users to enter latitude and longitude manually.
- **How to reproduce:** Attempt to search for a charging station using only an address.
- **Expected:** The application should convert the entered address into geographic coordinates.
- **Actual:** The original command-line application did not support address-based searches.
- **Resolution:** Added `geocoding.py`, which uses OpenStreetMap Nominatim to convert addresses and locations into coordinates.

### 3. Charging Power Parsing

- **Problem:** Charging power initially displayed as `Unknown` for all live stations because the ArcGIS charging-unit data was not being parsed correctly.
- **How to reproduce:** Search for a location and apply a minimum charging-speed filter.
- **Expected:** The application should extract numeric charging power values from the ArcGIS records.
- **Actual:** The initial parser did not correctly interpret the nested charging-unit data.
- **Resolution:** Updated the parsing logic to extract numeric power values from the charging-unit data. Verified that the minimum 50 kW filter returned 12 matching stations in the Iowa State University test.

### 4. Connector Type Filtering

- **Problem:** The CCS connector filter initially returned no matching stations because the filter value did not match the connector codes used by the ArcGIS dataset.
- **How to reproduce:** Search for a location and select CCS as the connector type.
- **Expected:** Stations supporting CCS connectors should appear in the results.
- **Actual:** The initial connector mapping returned zero matches.
- **Resolution:** Updated the connector mapping to use the ArcGIS value `J1772COMBO`. The CCS filter subsequently returned 14 matching stations in the Iowa State University test.

### 5. Invalid Address Handling

- **Problem:** The application needed to handle addresses that could not be found by the geocoding service.
- **How to reproduce:** Enter an invalid location, such as `zzzznotareallocation12345`.
- **Expected:** The application should display a helpful message without crashing.
- **Actual:** The application initially needed additional handling for unsuccessful geocoding results.
- **Resolution:** Added a user-facing message: "We couldn't find that location. Try entering a more specific address." Verified that the application handles this case without crashing.

## Version 2 Testing Notes

Testing was conducted using Iowa State University in Ames, Iowa, as the search location.

| Test | Result |
|---|---|
| Address geocoding | Passed |
| Live ArcGIS station retrieval | Passed — 47 stations returned |
| Map display | Passed |
| Available-only filter | Passed — 43 stations returned |
| CCS connector filter | Passed — 14 stations returned |
| Minimum charging power (50 kW) | Passed — 12 stations returned |
| Maximum distance (5 miles) | Passed — 25 stations returned |
| Invalid address handling | Passed |
| Pricing filter | Limited — no pricing values were available in the 47 returned records |

## Format for Future Bugs

- **Problem:**
- **How to reproduce:**
- **Expected:**
- **Actual:**
- **Status:**