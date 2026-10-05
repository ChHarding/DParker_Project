## Current issues

- The ArcGIS service does not always provide a simple numeric price-per-kWh value, so the price filter may show `Unknown` for some stations.
- Charging power is taken from the ArcGIS charging-unit data when a numeric power value is available. If it is missing, the program displays `Unknown` and a minimum-power filter will exclude that station.
- Real-time charger availability is not guaranteed by the station dataset. The app uses the station status/access fields provided by the data source rather than claiming a charger is currently free.
- The live ArcGIS service depends on an internet connection. If the service cannot be reached, the program falls back to the local sample dataset.

## Format for future bugs

- **Problem:**
- **How to reproduce:**
- **Expected:**
- **Actual:**
- **Status:**
