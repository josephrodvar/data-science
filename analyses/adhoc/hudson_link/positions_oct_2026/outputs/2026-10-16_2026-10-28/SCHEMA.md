# Hudson Link, Oct 16–28 2026: output schema

Two sets of CSVs, both written by `analysis.ipynb`:

- `data/`: the processed tables from `process.ipynb` (CSV versions of `data/processed/*/data.parquet`), filtered to the window.
- `charts/tables/`: the tables behind each chart in `charts/`.

Window is service days 2026-10-16 → 2026-10-28. `start_date` is the GTFS service day as `YYYYMMDD`; `service_date` is the local date the frame was recorded (differs from `start_date` for trips past midnight). `*_t` columns are UTC epoch seconds; `*_time` columns are the same instant in New York local time. Durations are minutes unless a column ends `_s` (seconds). Data caveats are in the project `AGENTS.md`.

Sources: Hudson Link real-time feed (CoachUSA) recorded via gtfs.zone; schedule from the 511NY GTFS.

# Processed data (`data/`)

"source" = CoachUSA's own prediction passed through; "gtfs.zone" (`est`) = schedule plus a delay estimated from GPS alone.

## `positions.csv` (frame × vehicle)
| column | description |
|---|---|
| `service_date` | Local date of the recorded frame. |
| `frame_t`, `frame_time` | Poll cycle time (about every 60 s). |
| `trip_key` | `trip_id|start_date`. |
| `trip_id`, `start_date`, `route_id` | Trip, service day, route. |
| `vehicle_id`, `label` | Bus id and display label. |
| `lat`, `lon` | GPS fix. |
| `gps_t` | Time of the GPS fix. |
| `gps_age_s` | `frame_t − gps_t`: how stale the fix was. |
| `bearing` | Heading, degrees. |
| `source_next_seq`, `source_next_delay_s` | Next stop (GTFS stop sequence) and its delay (s) per the source. |
| `est_next_seq`, `est_delay_s` | Same, per gtfs.zone. |
| `n_predicted_stops` | Remaining stops with a prediction. |

## `predictions.csv` (frame × vehicle × remaining stop)
| column | description |
|---|---|
| `service_date`, `frame_t`, `frame_time` | When the prediction was published. |
| `trip_key`, `vehicle_id`, `route_id` | Trip and bus. |
| `stop_sequence`, `stop_id` | Stop the prediction is for. |
| `sched_t` | Scheduled time at the stop. |
| `source_pred_t` | Source predicted arrival. |
| `source_delay_s` | Source delay (`source_pred_t − sched_t`). |
| `raw_sched_t`, `raw_est_t`, `raw_act_t` | Raw CoachUSA record's scheduled, estimated and actual times (empty when absent). |
| `est_pred_t` | gtfs.zone predicted arrival. |
| `actual_arr_t`, `actual_dep_t` | Hindsight arrival/departure inferred from the day's GPS. |
| `actual_approx` | `True` if interpolated rather than a fix within 100 m of the stop. |
| `actual_t` | Actual time used for scoring. |
| `horizon_s` | `actual_t − frame_t`: how far ahead the prediction was made. |
| `source_err_s`, `est_err_s` | Prediction − actual (s). Positive = predicted too late (bus came earlier). |
| `source_differs_from_raw` | The published source time differs from the raw CoachUSA time. |

## `stop_events.csv` (trip × vehicle × stop)
| column | description |
|---|---|
| `service_date`, `trip_key`, `trip_id`, `start_date`, `route_id`, `shape_id` | Trip identity. |
| `stop_sequence`, `stop_id`, `stop_name` | Stop. |
| `sched_t`, `sched_time` | Scheduled time. |
| `vehicle_id` | Bus that served it. |
| `actual_arr_t/_time`, `actual_dep_t/_time` | Hindsight arrival/departure (empty if not observed). |
| `actual_approx` | Interpolated, not a nearby fix. |
| `arr_delay_s`, `dep_delay_s` | Actual − scheduled (s). Positive = late. |

## `scheduled_trips.csv` (GTFS trip × service day)
| column | description |
|---|---|
| `trip_id`, `start_date` | Trip and service day. |
| `route_id`, `service_id`, `trip_headsign`, `trip_short_name`, `direction_id`, `block_id`, `shape_id`, `wheelchair_accessible`, `bikes_allowed` | Standard 511NY GTFS `trips.txt` fields. |

## `frames.csv` (poll cycle)
| column | description |
|---|---|
| `service_date`, `frame_t`, `frame_time` | Poll time. |
| `err` | Upstream API error that cycle (empty if OK). |
| `n_vehicles` | Vehicles matched to a trip. |
| `n_unresolved` | Raw vehicles with nothing published. |

## `flags.csv` (episodes from the recorder's issue detector)
| column | description |
|---|---|
| `service_date`, `t`, `end`, `start_time`, `end_time` | Episode start and end. |
| `kind` | `jump`: upstream next-stop delay moves ≥5 min between frames. `behind`: upstream's next stop is behind where the GPS projects for ≥2 min (missed-stop signal). `diverge`: source vs gtfs.zone ≥5 min apart. `shared`: one trip published for two vehicles. `unresolved`: raw vehicle with nothing published. |
| `trip`, `trip_key`, `vehicle_id` | Trip and bus. |
| `up`, `est` | Upstream and gtfs.zone delay values (s), for `diverge`/`jump`. |
| `max`, `ours_next`, `est_next`, `from`, `to` | Kind-specific detail (next-stop sequences, size of a jump); empty when not applicable. |

# Chart tables (`charts/tables/`)

## Chart 1: `trips_scheduled_vs_observed.png`

### `trips_scheduled_vs_observed.csv` (one row per service day)
| column | description |
|---|---|
| `start_date` | Service day. |
| `scheduled` | Trips in the 511NY schedule that day. |
| `observed` | Scheduled trips that showed up in the feed with a live vehicle. |
| `not_observed` | `scheduled − observed` (not run, or not tracked). |
| `pct_observed` | `observed / scheduled`, 0–1. |

### `scheduled_trips_observed.csv` (one row per trip × service day; underlying table)
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
