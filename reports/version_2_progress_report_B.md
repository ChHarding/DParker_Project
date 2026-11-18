Version 2 Progress Report B

Project Overview

Version 2 of the Electric Vehicle Charging Station Locator is all about taking the original command line application and turning it into a proper GUI. As a result of the professor's feedback it now uses Streamlit and address based geocoding so that users can search for EV charging stations in the vicinity without having to type in lat/long themselves.

Changes and Implementation

The following updates have been completed:

* Streamlit interface: the original command line interaction has been replaced with a Streamlit app.
* Application entry point: renamed main.py to app.py to support the new app structure.
* Address geocoding: Added geocoding.py, which uses the OpenStreetMap Nominatim service to convert user-entered addresses and locations into geographic coordinates.
* Live station data: Still using the ArcGIS Alternative Fueling Stations feature service to get the station data.
* Interactive map: Added a map showing the charging stations in the area around the location you searched for.
* Filtering: Implemented filters for distance, connector type, minimum charging power, maximum price, and station availability status.
* Data parsing: Updated the app to correctly parse the charging power from the ArcGIS charging unit data.
* Error handling: significantly improved handling of invalid addresses and unsuccessful API requests.
* Dependencies and documentation: requirements.txt, README.md and bugs.md have all been updated to reflect the Version 2 implementation and the test results.

Testing and Results

Testing was carried out using Iowa State University in Ames, IA as the search location.

The application successfully:

* Converted the entered location to lat/long coordinates.
* Retrieved 47 charging stations from the live ArcGIS service.
* Displayed the station locations on the map.
* Returned 43 stations when the available only filter was applied.
* Returned 14 stations when filtering for CCS connectors.
* Returned 12 stations when we applied a minimum charging power of 50kW.
* Returned 25 stations within a 5 mile distance filter.
* Displayed the correct error message when an invalid address was entered.

The maximum price filter was also tried. Of the 47 station records returned there was not a single one that had a price in it so a positive match couldn't be confirmed.

Additional testing details and the issues that have been resolved are all in bugs.md.

Current Limitations

There are a few limitations related to the available data:

* Pricing info: The ArcGIS dataset didn't provide price per kWh for the 47 stations that came back during the testing. Any stations with unknown pricing are filtered out when a max price filter is applied.
* Real-time availability: The dataset provides station status and access information, but does not guarantee real-time charger or port availability.
* Internet connectivity: Address geocoding and live station retrieval require an internet connection. The application can fall back to its local sample dataset if the ArcGIS service is unavailable, but address searches still require the geocoding service.

Next Steps

The next steps are to carry on with the testing and tuning of the Streamlit interface, go through the app structure and deal with any other issues that come up during the testing.

I'd also be interested in some feedback on whether the current approach to dealing with the missing pricing data is acceptable, or indeed whether we should be looking at a different data source as a potential alternative down the line.

Summary

Version 2 has successfully taken the original command line app and turned it into a Streamlit app with address geocoding, live charging station data, map display and filtering. The core functionality is in place and has been tested, the only real limitations being those of the data source itself.