"""Folium map helpers shared by the Bluebikes station notebooks."""

from __future__ import annotations

from pathlib import Path

import folium
import yaml

# bluebikes/ -> runbooks/ -> analyses/ -> repo root
CONFIG_SECRETS_PATH = Path(__file__).resolve().parents[3] / "config_secrets.yml"


def load_carto_api_key():
    if not CONFIG_SECRETS_PATH.exists():
        print("Warning: config_secrets.yml not found; CARTO map tiles may be rate-limited. See config_secrets_template.yml.")
        return None
    secrets = yaml.safe_load(CONFIG_SECRETS_PATH.read_text()) or {}
    key = secrets.get("api_keys", {}).get("carto")
    if not key:
        print("Warning: no CARTO api key set in config_secrets.yml; map tiles may be rate-limited.")
    return key


def base_map(lats, lngs, zoom_start=13):
    """CARTO Positron map centered on the mean of the given coordinates."""
    tiles = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
    carto_api_key = load_carto_api_key()
    if carto_api_key:
        tiles += f"?key={carto_api_key}"

    center = [sum(lats) / len(lats), sum(lngs) / len(lngs)]
    return folium.Map(location=center, zoom_start=zoom_start, tiles=tiles, attr="CARTO")


def add_station_marker(station_map, lat, lng, color, popup_html, tooltip, radius=8):
    folium.CircleMarker(
        location=[lat, lng],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.85,
        weight=2,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=tooltip,
    ).add_to(station_map)


def add_legend(station_map, colors_by_label):
    """Fixed bottom-left legend of colored dots, one per {label: color}."""
    legend_items = "".join(
        f'<div><span style="display:inline-block;width:10px;height:10px;'
        f'border-radius:50%;background:{color};margin-right:6px;"></span>'
        f"{label}</div>"
        for label, color in colors_by_label.items()
    )
    legend_html = f"""
<div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999;
            background: white; padding: 10px 12px; border: 1px solid #ccc;
            border-radius: 4px; font-size: 12px; font-family: sans-serif;">
{legend_items}
</div>
"""
    station_map.get_root().html.add_child(folium.Element(legend_html))
