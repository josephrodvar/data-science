# template_fetch_data

Template for pulling data from a live/open API rather than importing a
local file. Fetches trailing-12-month daily precipitation for NYC from the
Open-Meteo Historical Weather API (no key required), caches the raw pull
under `data/raw/`, aggregates to weekly totals, and charts it.

Copy this folder as the starting point for a new API-fetch analysis and
swap in the relevant source/params.
