# bike_accessibility

How far can you get from Brookline Village (approx. home) by bike vs e-bike
in 5 / 10 / 15 / 20 minutes?

`analysis.ipynb` uses the simplest definition — straight-line circles with
radius = assumed average speed × time — and renders a Folium map with one
radio-button layer per time band (bike + e-bike circle each). The map is
also saved to `outputs/bike_accessibility_map.html`. The final cell lists
ways to make it more realistic (network isochrones, elevation, calibrated
speeds from Bluebikes trips).
