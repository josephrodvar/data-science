# Hudson Link, Oct 16–28 2026: chart data schema

CSVs behind the charts in `../charts/`, written by `analysis.ipynb`. Window is service days
2026-10-16 → 2026-10-28. `start_date` is the GTFS service day as `YYYYMMDD`. Times in minutes
unless a column says `_s` (seconds). Data caveats are in the project `AGENTS.md`.

Sources: Hudson Link real-time feed (CoachUSA) recorded via gtfs.zone; schedule from the 511NY GTFS.

## Chart 1: `trips_scheduled_vs_observed.png`

### `trips_scheduled_vs_observed.csv` (one row per service day)
| column | description |
|---|---|
| `start_date` | Service day. |
| `scheduled` | Trips in the 511NY schedule that day. |
| `observed` | Scheduled trips that showed up in the feed with a live vehicle. |
| `not_observed` | `scheduled − observed` (not run, or not tracked). |
| `pct_observed` | `observed / scheduled`, 0–1. |

### `scheduled_trips.csv` (one row per trip × service day; underlying table)
| column | description |
|---|---|
| `start_date` | Service day. |
| `trip_id` | 511NY GTFS trip id. |
| `observed` | `True` if the trip appeared in the feed with a vehicle that day. |
| `route_id` | Route (H01–H07X). |
| `service_id` | GTFS service calendar id. |
| `trip_headsign` | Destination sign text. |
| `trip_short_name` | GTFS short name; empty in this feed. |
| `direction_id` | GTFS direction (0/1). |
| `block_id` | Vehicle block the trip belongs to. |
| `shape_id` | GTFS shape the trip follows. |
| `wheelchair_accessible` | GTFS flag (0 = no info). |
| `bikes_allowed` | GTFS flag (0 = no info). |

## Chart 2: `eta_completeness_scorecard.png`
Method: Swiftly ETA Completeness Benchmark. A scheduled trip-stop is *complete* when the trip had
an assigned vehicle and at least one prediction was published 0–15 min before the stop. This feed
never publishes CANCELED/SKIPPED, so `canceled_or_skipped` is always `False`.

### `eta_completeness_trip_stops.csv` (one row per scheduled trip × day × stop; underlying table)
| column | description |
|---|---|
| `trip_id`, `start_date` | Trip and service day. |
| `route_id` | Route. |
| `stop_sequence` | GTFS stop order within the trip. |
| `has_vehicle` | A vehicle was assigned to the trip that day. |
| `has_pred_0_15` | A prediction was published 0–15 min before the stop. |
| `canceled_or_skipped` | Always `False` here. |
| `complete` | `(has_vehicle and has_pred_0_15) or canceled_or_skipped`. |
| `reason` | `complete`, `no_vehicle`, or `no_pred_0_15` (vehicle, but no prediction in range). |

### `eta_completeness_outcomes.csv` (headline breakdown)
| column | description |
|---|---|
| `reason` | Outcome, as in `reason` above. |
| `trip_stops` | Count of scheduled trip-stops with that outcome. |

### `eta_completeness_by_day.csv` / `eta_completeness_by_route.csv`
| column | description |
|---|---|
| `start_date` / `route_id` | Grouping key (one file each). |
| `score` | `complete / scheduled`, 0–1. Tiers: ≥0.95 best in class, ≥0.90 good, ≥0.85 fair. |
| `complete` | Complete trip-stops. |
| `scheduled` | Scheduled trip-stops. |

## Chart 3: `prediction_error_by_horizon.png`
Every published CoachUSA ("source") prediction for a stop the bus later reached, 0–60 min ahead.
Error is **actual − predicted** arrival: positive = bus later than shown, negative = earlier (worse
for riders). "Actual" is inferred from ~1-minute GPS, so errors under ~1 min are noise.

### `prediction_error_by_horizon.csv` (one row per whole minute before arrival)
| column | description |
|---|---|
| `horizon_min` | Minutes between publishing the prediction and the actual arrival (0–59). |
| `p10`, `p25`, `median`, `p75`, `p90` | Percentiles of error, in minutes. p25–p75 is the "middle 50%" band, p10–p90 the "middle 80%". |
| `predictions` | Predictions in that minute. |

### `prediction_error_by_bucket.csv` (summary table)
| column | description |
|---|---|
| `bucket` | Horizon bucket: `0-5 min`, `5-15 min`, `15-30 min`, `30-60 min`. |
| `predictions` | Predictions in the bucket. |
| `mae_min` | Mean absolute error, minutes. |
| `median_min` | Median signed error (actual − predicted), minutes. |
| `p90_abs_min` | 90th percentile of absolute error, minutes. |
| `within_2_min` | Share with absolute error ≤ 2 min, 0–1. |
| `bus_2plus_min_early` | Share where the bus arrived more than 2 min before predicted, 0–1. |
