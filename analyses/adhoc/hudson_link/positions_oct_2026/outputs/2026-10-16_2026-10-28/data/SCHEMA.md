# Hudson Link, Oct 16–28 2026: processed data schema

CSV versions of `data/processed/*/data.parquet`, filtered to the window, written by `analysis.ipynb`.

Window is service days 2026-10-16 → 2026-10-28. `start_date` is the GTFS service day as `YYYYMMDD`; `service_date` is the local date the frame was recorded (differs from `start_date` for trips past midnight). `*_t` columns are UTC epoch seconds; `*_time` columns are the same instant in New York local time. Durations are minutes unless a column ends `_s` (seconds). Data caveats are in the project `AGENTS.md`.

Sources: Hudson Link real-time feed (CoachUSA) recorded via gtfs.zone; schedule from the 511NY GTFS.


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
