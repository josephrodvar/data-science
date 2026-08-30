# template_fetch_data

Template for pulling data from an open API rather than importing a local
file. Fetches trailing-12-month daily precipitation for NYC from the
Open-Meteo Historical Weather API (no key required), aggregates to weekly
totals, and charts it.

This is the reference example for the **load-or-fetch** pattern: the notebook
checks `data/raw/open_meteo_precipitation/{start}_{end}/data.csv` first and
only calls the API if that cache doesn't exist yet, writing it once it does.
Re-running the notebook for the same range is instant and hits the network
zero times. Copy this folder as the starting point for a new API-fetch
analysis, keep the check-cache-then-fetch shape, and swap in the relevant
source/params.
