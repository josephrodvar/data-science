# bluebikes

Repeatable runbook for tracking monthly Bluebikes ridership (total trips per
month) over a specified month range. Pulls monthly trip-history zips from
the [Bluebikes/Hubway S3 data bucket](https://s3.amazonaws.com/hubway-data/index.html)
(named `{YYYYMM}-bluebikes-tripdata.zip`, available from `201805` onward),
caches each month's extracted CSV under `data/raw/`, and plots a seaborn
line of monthly ridership across the range. Change the `MONTH_START` /
`MONTH_END` params (`YYYY-MM`) in the params cell to re-run for a different
range.

`analysis_yoy.ipynb` overlays the same range against the prior year, month
for month.

`new_stations.ipynb` takes a single `MONTH` param (`YYYY-MM`, defaults to the
latest complete calendar month) and finds stations whose `start_station_name`
appears that month but not in the month before — i.e. stations that opened
that month. Plots them on a Folium map (`outputs/{month}/new_stations_map.html`)
using `start_lat`/`start_lng`; each marker's popup shows days used in the
month, average daily ridership, and the station's ridership rank among all
stations that month.

`analysis_top_stations.ipynb` takes a single `MONTH` param (`YYYY-MM`,
defaults to the latest complete calendar month) and ranks stations by
average daily ridership separately for weekdays and weekends, writing the
top 10 of each to a Markdown report (`outputs/{month}/top_stations_report.md`)
and plotting their union on a Folium map
(`outputs/{month}/top_stations_map.html`). Markers are colored by whether a
station ranks top 10 on weekdays only, weekends only, or both (gold); every
popup shows the station's weekday and weekend ridership and rank regardless
of category.
