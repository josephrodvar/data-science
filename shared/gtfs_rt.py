"""Helpers for pulling and flattening GTFS-Realtime feeds.

Currently only unpacks VehiclePositions entities; extend as other feed
types (trip updates, alerts) actually get used in an analysis.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests
import yaml
from google.transit import gtfs_realtime_pb2

_AGENCIES_PATH = Path(__file__).parent / "agencies.yaml"


def load_agencies() -> dict:
    return yaml.safe_load(_AGENCIES_PATH.read_text())


def get_single_pull(
    agency: str, feed: str = "vehicle_positions", timeout: int = 30
) -> pd.DataFrame:
    """Fetch one GTFS-RT .pb feed and flatten its vehicle positions to a DataFrame."""
    config = load_agencies()[agency]
    url = f"{config['base_url'].rstrip('/')}/{config['feeds'][feed]}"

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    feed_message = gtfs_realtime_pb2.FeedMessage()
    feed_message.ParseFromString(response.content)

    rows = []
    for entity in feed_message.entity:
        if not entity.HasField("vehicle"):
            continue
        vehicle = entity.vehicle
        rows.append(
            {
                "vehicle_id": vehicle.vehicle.id,
                "trip_id": vehicle.trip.trip_id,
                "route_id": vehicle.trip.route_id,
                "lat": vehicle.position.latitude,
                "lon": vehicle.position.longitude,
                "bearing": vehicle.position.bearing
                if vehicle.position.HasField("bearing")
                else None,
                "timestamp": vehicle.timestamp,
            }
        )

    return pd.DataFrame(rows)
