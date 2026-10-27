"""maag — mobility at a glance.

Prints next departures for the Green Line (eastbound from Brookline Village)
and the 66 (northbound from stop 1369), plus Bluebikes availability at the
home stations. All live: MBTA V3 predictions + Bluebikes GBFS.
"""

from __future__ import annotations

from datetime import datetime, timezone

from shared.api import get

MBTA_API = "https://api-v3.mbta.com"
GBFS_URL = "https://gbfs.bluebikes.com/gbfs/gbfs.json"
N_DEPARTURES = 3

# direction_id: Green-D 1 = East (toward Union Sq); 66 0 = Outbound (toward Harvard)
TRANSIT = [
    {"icon": "🚋", "label": "Green Line E-bound @ Brookline Village", "stop": "place-bvmnl", "route": "Green-D", "direction_id": 1},
    {"icon": "🚌", "label": "66 N-bound @ Harvard St & Aspinwall", "stop": "1369", "route": "66", "direction_id": 0},
]
HOME_STATION_NAMES = ["99 Harvard St", "Brookline Town Hall", "Brookline Village MBTA at Pearl Street"]


def next_departures(stop: str, route: str, direction_id: int, now: datetime) -> list[int]:
    """Minutes until the next departures, soonest first."""
    payload = get(
        MBTA_API,
        "predictions",
        params={
            "filter[stop]": stop,
            "filter[route]": route,
            "filter[direction_id]": direction_id,
            "sort": "departure_time",
        },
    )
    minutes = []
    for prediction in payload["data"]:
        departure = prediction["attributes"]["departure_time"]
        if departure is None:  # e.g. last stop / skipped
            continue
        seconds = (datetime.fromisoformat(departure) - now).total_seconds()
        if seconds >= 0:
            minutes.append(int(seconds // 60))
    return minutes[:N_DEPARTURES]


def bike_availability() -> list[dict]:
    feed_urls = {feed["name"]: feed["url"] for feed in get(GBFS_URL)["data"]["en"]["feeds"]}
    information = get(feed_urls["station_information"])["data"]["stations"]
    status = {s["station_id"]: s for s in get(feed_urls["station_status"])["data"]["stations"]}

    names = {s["station_id"]: s["name"] for s in information if s["name"] in HOME_STATION_NAMES}
    rows = []
    for station_id, name in sorted(names.items(), key=lambda kv: HOME_STATION_NAMES.index(kv[1])):
        s = status[station_id]
        ebikes = s.get("num_ebikes_available", 0)
        rows.append(
            {
                "name": name,
                "classic": s["num_bikes_available"] - ebikes,  # num_bikes_available includes e-bikes
                "ebikes": ebikes,
                "docks": s["num_docks_available"],
                "renting": bool(s["is_renting"]),
            }
        )
    return rows


def format_minutes(minutes: list[int]) -> str:
    if not minutes:
        return "no predictions"
    return ", ".join("now" if m == 0 else f"{m} min" for m in minutes)


def main() -> None:
    now = datetime.now(timezone.utc)
    print(f"maag — {now.astimezone():%a %b %-d, %-I:%M %p}\n")

    for t in TRANSIT:
        minutes = next_departures(t["stop"], t["route"], t["direction_id"], now)
        print(f"{t['icon']} {t['label']}: {format_minutes(minutes)}")

    print("\n🚲 Bluebikes")
    for b in bike_availability():
        flag = "" if b["renting"] else "  (not renting)"
        print(f"   {b['name']}: {b['classic']} classic, {b['ebikes']} e-bikes, {b['docks']} docks{flag}")


if __name__ == "__main__":
    main()
