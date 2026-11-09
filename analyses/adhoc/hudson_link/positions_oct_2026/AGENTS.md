# hudson_link / positions_oct_2026

How well did Hudson Link (Lower Hudson Transit Link, the CoachUSA-run express
buses H01–H07X across the Cuomo Bridge between Rockland and Westchester)
perform Oct 12–29 2026? Questions: fleet size, frequency, schedule
adherence, missed trips, and how good the real-time arrival predictions were.

- `process.ipynb` flattens the replay JSON into `positions` (the unified
  frame × vehicle table), `predictions`, `stop_events`, `frames` and `flags`.
  It also fetches the 511NY GTFS into `data/raw/gtfs_schedule/` and builds
  `scheduled_trips`. Everything lands in `data/processed/`. Run it first.
- `analysis.ipynb` has one section per metric, limited to service days
  **Oct 16–28** (the clean window, see below):
  1. Trips scheduled vs observed.
  2. ETA completeness, per the Swiftly ETA Completeness Benchmark (complete
     trip-stops / scheduled trip-stops), with a PNG scorecard.
  3. Prediction accuracy by horizon.

  It ends with a list of next metrics. Charts are saved to
  `outputs/2026-10-16_2026-10-28/charts/`.

## Where the data comes from (`reference/`, not used by the notebook)

A friend (Max) built a recorder for gtfs.zone, a service that republishes
small agencies' real-time data as GTFS-Realtime. The recorder ran the real
Hudson Link poller every ~60 s without publishing. Each cycle it saved the raw
CoachUSA tracker responses plus the trip updates the poller computed from
them. A `build.py` (not included) turned that into one `replay/*.json` per
local day, now in `data/raw/replay/`. Each file has the frames, each vehicle's
GPS fix and per-stop predictions, trip schedules, flags, and hindsight
"actual" stop times inferred from the day's GPS (fix within 100 m of the stop,
else an interpolated crossing marked `approx`).

Two predictions are compared throughout:
- **source**: CoachUSA's own ETA, passed through (what riders see).
- **gtfs.zone**: schedule plus a delay estimated from GPS position alone.

The files in `reference/`:
- `max-notes.md`: the friend's lab notebook, the most useful file.
- `analyze.py`: MAE by horizon, source vs gtfs.zone.
- `viewer.html`: map and slider replay viewer.
- `README.txt`

The viewer and `analyze.py` expect `replay/` next to them, so they won't
run from here without moving files back. Main findings in the notes:
- CoachUSA predictions beat gtfs.zone's at every horizon, so the source is kept.
- CoachUSA delays sometimes jump 4–6 min between polls.
- CoachUSA keeps listing the origin as "next stop" after the bus has left (`behind` flag).
- The upstream API failed 35 cycles (Oct 20, 21, 27).

Data caveats:
- **Oct 13 – Oct 15 19:19 ET are nearly empty.** A recorder bug dropped
  today's journeys when yesterday ran the same trip. Oct 12 starts at
  07:30, and Oct 29 ends partway through the day.
- The trip ids come from the **511NY** feed. The Trillium feed on Mobility
  Database uses different ids and has wrong times, so don't use it.
- The GTFS is the current 511NY zip (`feed_version` S1000138, valid
  2026-06-01 → 2027-06-28), not an archived October copy. All replay
  trip ids match it.
- The notes also cover a second source (buswhere / Columbia County) that
  isn't in this folder's replay data.
