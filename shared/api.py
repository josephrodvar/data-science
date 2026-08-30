"""Minimal HTTP GET wrapper: a base URL plus params, nothing more.

This is deliberately thin — a starting shape for hitting a JSON API. Real
sources will likely need their own variant (pagination, auth headers,
retries, rate limits) as those needs actually show up; don't generalize
this ahead of that need.
"""

from __future__ import annotations

import requests


def get(
    base_url: str,
    path: str = "",
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int = 30,
):
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}" if path else base_url
    response = requests.get(url, params=params, headers=headers, timeout=timeout)
    response.raise_for_status()

    if "json" in response.headers.get("Content-Type", ""):
        return response.json()
    return response
