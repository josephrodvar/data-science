"""Prediction accuracy of source vs gtfs.zone against GPS hindsight, from replay/*.json.

Usage: python3 scratch/analyze.py [source ...]
Per prediction (frame, vehicle, future stop with an `actual` time) compares
source = our published time, gtfs.zone = scheduled + estimator delay, both
only where the other exists too. Buckets by horizon (actual - frame time).
"""

import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
BUCKETS = [(0, 300), (300, 900), (900, 1800), (1800, 3600), (3600, 10800)]


def bucket(h):
    for lo, hi in BUCKETS:
        if lo <= h < hi:
            return f"{lo // 60:>3}-{hi // 60:<3}m"
    return None


def stats(errs):
    if not errs:
        return "-"
    a = sorted(abs(e) for e in errs)
    return (
        f"n={len(errs):>6} mae={sum(a) / len(a) / 60:5.1f} "
        f"med={a[len(a) // 2] / 60:4.1f} p90={a[int(len(a) * 0.9)] / 60:5.1f} "
        f"bias={statistics.mean(errs) / 60:+5.1f}"
    )


def analyze(source):
    files = sorted(HERE.glob(f"replay/{source}-*.json"))
    by_bucket = defaultdict(lambda: ([], []))
    by_day = defaultdict(lambda: ([], []))
    by_route = defaultdict(lambda: ([], []))
    exact_only = defaultdict(lambda: ([], []))
    mismatch = [0, 0]
    trips_per_day = {}
    err_frames = {}
    wins = defaultdict(int)
    for f in files:
        d = json.loads(f.read_text())
        tz = ZoneInfo(d["tz"])
        trips_per_day[d["date"]] = len(d["trips"])
        err_frames[d["date"]] = sum(1 for fr in d["frames"] if fr["err"])
        actual = {
            k: {s[0]: (s[1] if s[1] is not None else s[2], s[3]) for s in v}
            for k, v in d["actual"].items()
        }
        wd = datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a")
        for fr in d["frames"]:
            t = fr["t"]
            for v in fr["v"]:
                key = f"{v['trip']}|{v['id']}"
                act = actual.get(key, {})
                trip = d["trips"][v["trip"]]
                sched = {s[0]: s[2] for s in trip["schedule"]}
                est = v["est"]
                for seq, ptime, _ in v["ours"]:
                    if seq not in act or seq not in sched or est is None or seq < est[1]:
                        continue
                    at, approx = act[seq]
                    if at is None or at < t:
                        continue
                    b = bucket(at - t)
                    if b is None:
                        continue
                    e_src = ptime - at
                    e_gz = sched[seq] + est[0] - at
                    for agg, k in (
                        (by_bucket, b),
                        (by_day, f"{d['date']} {wd}"),
                        (by_route, trip["route"]),
                    ):
                        agg[k][0].append(e_src)
                        agg[k][1].append(e_gz)
                    if not approx:
                        exact_only[b][0].append(e_src)
                        exact_only[b][1].append(e_gz)
                    wins["source" if abs(e_src) < abs(e_gz) else "gtfs.zone" if abs(e_gz) < abs(e_src) else "tie"] += 1
                # Translation: our time vs the raw upstream prediction.
                if source == "hudsonlink" and v["raw"]:
                    raw = {r[0]: r[4] or r[3] for r in v["raw"] if r[0]}
                    stop_of = {s[0]: s[1] for s in trip["schedule"]}
                    for seq, ptime, _ in v["ours"]:
                        r = raw.get(stop_of.get(seq))
                        if r is not None:
                            mismatch[1] += 1
                            mismatch[0] += r != ptime
        del d

    print(f"\n######## {source}  ({len(files)} days)")
    print("trips/day:", " ".join(f"{k[5:]}={v}" for k, v in trips_per_day.items()))
    print("error frames/day:", " ".join(f"{k[5:]}={v}" for k, v in err_frames.items() if v))
    if mismatch[1]:
        print(f"translation: {mismatch[0]}/{mismatch[1]} stop times differ from raw")
    print("closer per prediction:", dict(wins))
    for title, agg in (
        ("by horizon (all actuals)", by_bucket),
        ("by horizon (actual within 100 m only)", exact_only),
        ("by day", by_day),
        ("by route", by_route),
    ):
        print(f"\n-- {title}")
        for k in sorted(agg):
            s, g = agg[k]
            print(f"  {k:<24} source   {stats(s)}")
            print(f"  {'':<24} gtfs.zone {stats(g)}")


if __name__ == "__main__":
    for s in sys.argv[1:] or ["hudsonlink", "buswhere"]:
        analyze(s)
