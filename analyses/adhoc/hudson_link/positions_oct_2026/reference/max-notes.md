# Feed recording + replay (scratch)

Untracked. `scratch/` is ignored through `.git/info/exclude`, never commit it.

## Goal

Record about a week of Hudson Link and Columbia County (buswhere) data:
raw upstream responses plus the `VehicleUpdate`s our sources compute from them.
Then replay it in the browser to check:

1. Translation: raw -> ours (trip match, stop mapping, per-stop times).
2. Upstream delay quality: their delays go wrong when a bus "misses" a stop.
   Compare against gtfs.zone's position-based delay
   (`gtfs-zone-rt-delay-estimator` `trip_math.compute_progress`) to judge
   whether to replace theirs.

## Files

- `record.py`: runs the real source (`build_source` + `startup` + `fetch`)
  with an httpx response hook that captures every upstream response. Never
  publishes. One line per cycle in
  `data/<source>/cycles-YYYY-MM-DD.jsonl.gz` (UTC date):
  `{t, gtfs, error, raw: [{t, method, url, status, location, body}], updates: [VehicleUpdate...]}`.
  Each gzip line is its own member, so a killed process loses at most one line.
  Startup discovery traffic (hudsonlink searches) lands in the first cycle line.
- `data/<source>/starts.jsonl`: one line per process start (commit, gtfs sha8, interval).
- `data/<source>/gtfs-<sha8>.zip`: the GTFS each cycle was computed against
  (the `gtfs` field of a cycle line).
- `build.py`: recording -> `replay/<source>-<local date>.json` + `replay/index.json`.
  Per frame and vehicle: our update, the raw record it came from, and the
  estimator's delay/next stop (`trip_math` imported from the sibling
  delay-estimator repo). Flags (thresholds at the top of the file):
  `jump` upstream next-stop delay moves >= 5 min between frames; `behind`
  upstream's next stop is behind where the GPS projects for >= 2 min (the
  missed-stop signal); `diverge` upstream vs estimator >= 5 min; `shared` one
  trip published for two vehicles; `unresolved` raw vehicle with nothing
  published. Flags are per trip and vehicle. Also per day: route shapes
  (simplified) and route colors (feed colors only when distinct), and
  `actual` per trip+vehicle: `[seq, arrival, departure, approx]` from the
  whole day's GPS fixes. Fixes within 100 m of a stop give first/last as
  arrival/departure; else interpolated crossing of the stop on the stop
  polyline (`approx` = 1). Origin has departure only.
- `viewer.html`: map + slider replay, labelled "source" (upstream's
  prediction, passed through) vs "gtfs.zone" (estimator). Shapes colored per
  route (hashed hue when the feed has no distinct colors). Click a vehicle for
  its stop table (sched | source raw | source | gtfs.zone | actual; red cell =
  source != raw; (pred - actual) next to each prediction; MAE line over
  remaining stops) and its delay chart (source orange, gtfs.zone blue, flags
  shaded; click to seek). Arrow keys
  step (shift = 10), space plays. Flag list filters by kind and seeks.
- `replay_discovery.py`: re-runs hudsonlink discovery matching on a recorded
  cycle file (used to find the journey id bug).

## Running on kcfam

Code copy lives in `kcfam:~/rt-recording` (rsync of this repo, no `.git`).
uv is installed user-local in `~/.local/bin`.

```bash
# deploy / update
rsync -a --exclude .venv --exclude .git --exclude scratch/data ./ kcfam:~/rt-recording/
ssh kcfam 'cd ~/rt-recording && ~/.local/bin/uv sync'

# start (tmux session "rec", one window per source)
ssh kcfam 'bash ~/rt-recording/scratch/start.sh'

# check
ssh kcfam 'ls -la ~/rt-recording/scratch/data/*/; tail -3 ~/rt-recording/scratch/data/*.log'

# stop
ssh kcfam 'tmux kill-session -t rec'

# pull data back
rsync -a kcfam:~/rt-recording/scratch/data/ scratch/data/
```

## Viewing

```bash
rsync -a kcfam:~/rt-recording/scratch/data/ scratch/data/
uv run --with shapely python scratch/build.py      # or: build.py hudsonlink
cd scratch && python3 -m http.server 8765          # http://localhost:8765/viewer.html
```

## Log

- 2026-10-12: recorder written, smoke-tested locally against commit 584d3b1.
  Hudson Link: startup discovery ~40s, 1061 journeys, 714 trips matched, first
  cycle 52 raw responses (34 status calls), 14 updates. Buswhere: no active
  buses (Columbus Day, last update Fri Oct 9), so expect data from Oct 13.
- Side finding: `config.py`'s default buswhere `GTFS_URL`
  (`github.com/.../raw/...`) now 302s to raw.githubusercontent.com and
  `fetch_gtfs` doesn't follow redirects, so it fails with no cache. Infra sets
  the raw URL explicitly, so production is fine. `record.py` does the same.
- 2026-10-12 07:30 ET: uv installed on kcfam, both recorders started in tmux
  session `rec` via `scratch/start.sh` (restart loop, logs in
  `scratch/data/<source>.log`). First hudsonlink cycle: 54 raw, 13 updates.
  Discovery cycle line is ~0.9 MB gzipped, so expect about 1 MB/day of
  discovery plus status traffic.
- 2026-10-15 19:14 ET check-in: both recorders up since Mon, 0 restarts, 0
  cycle errors, 30 MB total. Buswhere: clean, 2-4 trips per hour Tue-Thu
  06:00-18:59, none Mon (holiday).
- Hudson Link BUG (affects production too): polling stopped Tue ~03:00 ET.
  Since then it only polls yesterday's late trips for ~1h after the midnight
  discovery. Cause: CoachUSA journey ids are per (trip, origin, destination)
  and reused across dates (633 of 984 ids seen on more than one date).
  `_discover` dedups with `journeys.setdefault(j.id, j)` and searches
  yesterday first, so today's journey is dropped whenever yesterday ran the
  same trip. Monday worked only because the process started Mon morning and
  Sunday's trips differ. Fix: key by `(j.id, j.origin_departure.date())`.
  Verified offline with `scratch/replay_discovery.py --fixed`: Tue and Wed
  midday trips_near 21/21 matched (was 0/21). Usable Hudson Link data so far:
  Mon Oct 12 07:30 to Tue 02:00 ET only.
- 2026-10-15: fixed in v0.4.1 (`56547ef`, tag pushed, image built). kcfam
  recorder restarted on it 19:19 ET with existing data kept. Infra pin bump to
  v0.4.1 staged in gtfs-zone-infra, not pushed yet.
- 2026-10-15: build.py + viewer.html working on Oct 12-15. First look:
  - Hudson Link Mon: upstream next-stop delay swings 4-6 min between 1-min
    polls on some trips (e.g. 741020: 0, -4, -10, -15, -10 min); 121
    `behind` episodes, mostly at stop 1 (upstream still lists the origin as
    next after the bus has left it).
  - Buswhere: two devices often resolve to the same trip (`shared`, e.g.
    C12 and C13 both on HUD_ALB_C_AM_SB, chatham 54742/55169 on HUD_CHT_1),
    since `resolve_by_route` only picks by route + time window. The second
    bus then gets a wrong schedule and huge delays (+27 min vs est -6).
  - Estimator struggles on loops (Shopping shuttle): projecting onto a
    polyline that starts and ends at the same place gives -54 min at the
    loop start.
- 2026-10-17: compared the two Hudson Link GTFS feeds (`gtfs_compare.py`):
  511NY (what we use) and Trillium
  (`data.trilliumtransit.com/gtfs/hudsonlink-ny-us/...`, built 2026-08-31).
  511NY matches every CoachUSA journey Oct 12-18 (same stops and first
  departure); Trillium matches 279/302 weekdays, 213/238 Sat, and only 5 on
  Columbus Day, where it runs the weekend schedule. GPS says 511NY is right:
  202 weekday-only trips ran on Oct 12; buses wait at 511NY's Monsey stop
  (Trillium's is 457 m off); H03 Monsey trips that Trillium moves by 3-10 min
  left at 511NY's times on most observed trips (3518, 3522, 3524, 3556, 3560).
  Trillium also has no stop_code, drops H07X 9x14/9x16 from Spring Valley and
  merges BRW287 into BR119. Weekend differences not yet checked against GPS
  (recording ended Sat 06:55 ET). Kept 511NY; reason in `docs/hudsonlink.md`.
- 2026-10-17: viewer reworded to source vs gtfs.zone, route shapes added, and
  hindsight `actual` stop times from GPS. First attempt (polyline crossing
  only) put 741020 at Palisades Lot J at 07:34; the bus loops the lot and
  projects past the stop. It actually sat there 07:37-07:51 (layover), which
  the 100 m proximity rule now catches. Fixed a viewer bug where the chart's
  gtfs.zone line never drew (unquoted `stroke-width=1.5/>` nested the second
  path inside the first).
- 2026-10-17: Hudson Link vehicles drawn as arrows along the source's
  `bearing` (kept in replay frames as `bearing`). Buswhere has no heading in
  its feed, so its vehicles stay dots.
- 2026-10-30: pulled Oct 12 to 30 (recorders up since Oct 15 19:19, 0
  restarts). Rebuilt replay, added `analyze.py` (source vs gtfs.zone
  predicted arrival against GPS hindsight `actual`, by horizon/day/route).
  - Hudson Link: source beats gtfs.zone at every horizon (MAE 1.6/2.5/3.5/5.2
    min at 0-5/5-15/15-30/30-60 min vs 1.8/2.7/4.3/7.4); gtfs.zone runs
    early (bias -4.6 min at 30-60). Keep upstream. Translation: 292 of 629k
    stop times differ from raw. Upstream 500s: 35 failed cycles (Oct 20, 21, 27).
  - Buswhere: gtfs.zone better (MAE 2.4/4.2/5.6/6.6 vs source 4.3/5.6/7.0/7.3,
    p90 at 0-5 min 5.4 vs 13.3). Gap is all Albany-Commuter (source MAE 8.5,
    bias +6.8 vs 4.6); Shopping is a wash.
  - Chatham-Hudson GTFS bug: service `TUES_FRI` has thursday=1, friday=0.
    Buses run Tue and Fri; both Fridays (Oct 16, 23) 09:00-14:00 unresolved.
  - Recurring weekday unmatched: hudson__albany_b_pm ~16:00 and _d_pm ~17:00
    every day; shopping_shuttle devices 54742/55168 unresolved ~15 h total.
- 2026-10-30: unmatched fixes.
  - columbia-county-gtfs branch `max/edit-gtfs-zone`: TUES_FRI now Tue+Fri;
    generator removed (zip edited in edit.gtfs.zone, validator workflow);
    route colors/short names, feed_version 2, Fares v2 from the 2022 rate
    sheet. Validator: 0 errors, 1 warning (Chatham short name in long name).
  - pollers branch `fix/buswhere-layover-match`: `resolve_by_route` falls
    back to the next trip starting within 20 min (`_LAYOVER_LEAD`).
  - `replay_buswhere.py` re-runs `BuswhereSource.fetch` on the recording:
    old feed + no lead reproduces the log exactly (chatham 2303, b_pm 813,
    d_pm 311, c_am 72, shopping 4 cycles); new feed + 20 min gives 0, shared
    counts unchanged.
  - `build.py` unresolved now keys on device across slugs (shopping echoes of
    Albany buses were false positives). Replay files still show the old
    poller output, since they are built from recorded updates.
  - Still open: `shared` (two devices on one trip), mostly SHOPPING_WK_*
    and HUD_ALB_D_PM_SB / C_AM_SB.
- 2026-10-30: shared trips. Replay (`scratch/replay_buswhere.py`, new feed,
  20 min lead) had 6631 shared device-cycles, all within one slug. buswhere's
  `current` is no tiebreaker: it often tracks a bus parked at the garage
  (42.2403,-73.7633). ETA fit (stops within 10 min of schedule) picks the
  loop bus in town, but Albany SB ETAs are junk (the SB bus keeps +25 min
  "next visit" ETAs to the Albany stops it passed), and Albany buses echoed
  into shopping can fit by chance. Distance to the trip's scheduled position
  separates those (real bus 1-5 km, other 13-44 km). Fix: drop devices more
  than 5 km further than the nearest, then best ETA fit. Shared 6631 -> 0.
  Still open: Albany SB predictions themselves (passed-stop ETAs survive the
  30 min skew filter), and lone echoed devices published on the wrong
  route's trip (e.g. C12 on SHOPPING_WK_1731 at 17:33 Oct 19).
