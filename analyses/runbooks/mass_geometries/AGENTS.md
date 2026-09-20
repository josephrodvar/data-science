# mass_geometries

Pulls Massachusetts town/county-subdivision boundary geometries from the
Census TIGER/Line dataset and plots them. Currently a single example view:
Brookline highlighted on a contextily basemap, but the underlying
`towns` GeoDataFrame covers every MA town and can be reused for other
municipal-boundary views.

Source: [TIGER/Line 2022 COUSUB shapefile for Massachusetts (state FIPS
25)](https://www2.census.gov/geo/tiger/TIGER2022/COUSUB/tl_2022_25_cousub.zip),
cached under `data/raw/tl_2022_25_cousub/` on first run.
