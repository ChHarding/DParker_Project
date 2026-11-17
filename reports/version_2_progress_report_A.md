# EV Charging Station Locator — Version 2 Progress Report A

**Project:** HCI 5840 — Electric Vehicle Charging Station Locator  
**Current version:** Version 2 Progress Report A

## Professor feedback addressed

The main feedback from Version 1 was to replace Python's `urllib`/`urlopen` request with the `requests` library because the live ArcGIS request produced an SSL certificate verification error. The professor also recommended continuing to improve error handling, validation, function structure, comments/docstrings, and testing rather than disabling SSL verification.

This checkpoint addresses that feedback by:

- Replacing `urllib.request.urlopen()` with `requests.get()`.
- Keeping normal SSL certificate verification enabled.
- Adding `response.raise_for_status()` for HTTP errors.
- Checking the ArcGIS JSON response for a service-level `error` object.
- Catching `requests` request failures and falling back to the local sample data.
- Adding explicit latitude and longitude upper bounds (`90` and `180`) in addition to lower bounds.
- Keeping the existing CLI workflow and sample-data fallback instead of rewriting the application.
- Adding Google-style documentation to the updated network and numeric-input functions.
- Adding `requirements.txt` so the external dependency is documented and reproducible.

## Work completed

The Version 2 work continues from the Version 1 code rather than creating a separate application. The primary source file remains `main.py`.

### ArcGIS request

The application now builds the same ArcGIS query parameters but sends them through `requests.get()`. A 15-second timeout is still used so the program does not wait indefinitely for the service.

The application now handles three broad types of live-service problems:

1. HTTP request errors.
2. ArcGIS service errors returned in a successful HTTP response.
3. JSON/OS-level problems while processing the response.

When the live request cannot be used, the existing local sample dataset remains available for testing.

### Input validation

Latitude and longitude are now validated against their real geographic ranges:

- Latitude: -90 through 90.
- Longitude: -180 through 180.

The existing numeric validation for filters remains in place.

### Project organization

A new `requirements.txt` file documents the `requests` dependency. The existing project structure, data folder, documentation folder, README, bug sheet, license, and sample data are retained.

## Testing completed

- Python syntax/compilation check was completed for the updated `main.py`.
- The project was reviewed to confirm the new `requests` import replaces the previous `urllib` request path.
- The existing sample-data fallback remains in the application.
- Live ArcGIS connectivity still needs to be tested on the development computer because the original SSL problem was environment-specific.

## Remaining work

1. Run the application locally and test whether `requests` resolves the original SSL certificate problem.
2. If the SSL error remains, follow the professor/Copilot-recommended macOS certificate troubleshooting rather than disabling SSL verification.
3. Test live ArcGIS records and confirm the returned fields map correctly to the application.
4. Exercise invalid latitude/longitude input and each search filter.
5. Improve or add comments/docstrings where additional refactoring is useful.
6. Record reproducible bugs and fixes in `bugs.md`.
7. Continue with the next Version 2 milestone after the live-data path is verified.

## Help requested

The most useful instructor feedback at this stage would be confirmation that the `requests`-based ArcGIS approach and current fallback/error-handling strategy are appropriate. If the SSL problem persists despite using `requests`, guidance on the expected development-environment certificate setup would also be helpful.

## Current status

**Version 2 Progress Report A:** The first reliability milestone is in progress. The code has been updated to follow the professor's recommendation to use `requests`, but successful live ArcGIS connectivity has not yet been confirmed on the development computer.
