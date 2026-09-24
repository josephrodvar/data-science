# bluebikes

Repeatable runbook for Bluebikes ridership and station activity, built on
the monthly trip-history zips in the
[Bluebikes/Hubway S3 data bucket](https://s3.amazonaws.com/hubway-data/index.html)
(named `{YYYYMM}-bluebikes-tripdata.zip`, available from `201805` onward).
Each month's extracted CSV is cached under
`data/raw/bluebikes_tripdata/{yyyymm}/data.csv`.

`analysis_ridership.ipynb` takes a `MONTH_START` / `MONTH_END` range
(`YYYY-MM`) and plots monthly ridership (total trips per month) across it,
plus a year-over-year overlay of the same range against the prior year,
month for month. Charts go to `outputs/{start}_{end}/charts/`.

`analysis_stations.ipynb` takes a single `MONTH` param (`YYYY-MM`, defaults
to the latest complete calendar month) and writes to `outputs/{month}/`:

- `all_stations_map.html` — every station active that month, sized by
  average daily ridership, with stations new that month highlighted.
- `new_stations_map.html` — stations whose `start_station_name` appears
  that month but not the month before, i.e. stations that opened.
- `top_stations_report.md` / `top_stations_map.html` — top 10 stations by
  average daily ridership, ranked separately for weekdays and weekends;
  map markers colored weekday-only, weekend-only, or both (gold).
  The report is posted to Slack only when `SEND_SLACK = True` (default
  `False`).

`plots.py` holds the shared Folium helpers (CARTO basemap, station marker,
legend) used by the station maps.

`gbfs/` pulls live snapshots of the Bluebikes GBFS feeds — see its own
`AGENTS.md`.
