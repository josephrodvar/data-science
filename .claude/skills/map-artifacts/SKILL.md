---
name: map-artifacts
description: Repo conventions for map visualizations (Folium interactive maps, contextily static basemaps) — fetching the CARTO API key from config_secrets.yml and using the Positron light basemap. Use whenever creating or editing a map in an analysis notebook.
---

# Map artifacts

Repo-wide conventions for maps, whether interactive (Folium) or static
(contextily + matplotlib).

## Basemap

Default to **CARTO Positron** (light, minimal) for every map unless the
analysis has a specific reason to use something else:

- Folium: `folium.Map(..., tiles="cartodbpositron")`
- contextily: `ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)`

## CARTO API key

CARTO basemap tiles need an API key. Load it from `config_secrets.yml` at
the repo root (gitignored — see `config_secrets_template.yml` for the shape
to copy), never hardcode it in a notebook:

```python
import yaml

def load_carto_api_key():
    path = Path("config_secrets.yml")
    if not path.exists():
        print("Warning: config_secrets.yml not found; CARTO map tiles may be rate-limited.")
        return None
    key = (yaml.safe_load(path.read_text()) or {}).get("api_keys", {}).get("carto")
    if not key:
        print("Warning: no CARTO api key set in config_secrets.yml; map tiles may be rate-limited.")
    return key
```

Resolve the path relative to the repo root (walk up from the notebook, or
use a fixed relative `../../../config_secrets.yml` depth) since notebooks
live several levels deep under `analyses/`.

Append the key to the tile URL rather than passing it as a separate
`folium.Map` argument — Folium doesn't have a dedicated CARTO-key param:

```python
tiles = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
if carto_api_key:
    tiles += f"?key={carto_api_key}"

folium.Map(location=map_center, zoom_start=13, tiles=tiles, attr="CARTO")
```

Missing key: warn (as above) and continue with the unauthenticated tile
URL rather than failing the notebook — anonymous CARTO tiles still work at
low volume.
