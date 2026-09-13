# bluebikes_ridership

Repeatable runbook for tracking monthly Bluebikes ridership (total trips per
month) over a specified month range. Pulls monthly trip-history zips from
the [Bluebikes/Hubway S3 data bucket](https://s3.amazonaws.com/hubway-data/index.html)
(named `{YYYYMM}-bluebikes-tripdata.zip`, available from `201805` onward),
caches each month's extracted CSV under `data/raw/`, and plots a seaborn
line of monthly ridership across the range. Change the `MONTH_START` /
`MONTH_END` params (`YYYY-MM`) in the params cell to re-run for a different
range.
