---
name: chart-style
description: Repo conventions for matplotlib/seaborn charts in this workspace — apply_theme import, tick-label formatting (comma-separated thousands, 3-letter month dates), axis-label rules, and title punctuation. Use whenever creating or editing a chart in an analysis notebook.
---

# Chart style

Repo-wide conventions for charts built with `shared/plots/style.py`. Apply
these whenever writing or editing a plotting cell.

## Setup

Always import and call the shared theme before plotting:

```python
from shared.plots.style import apply_theme, add_source_footnote

apply_theme()
```

## Source footnote

Every chart gets a source footnote — this is not optional. Explicitly name
where the data came from (the portal, API, or file), not a generic label:

```python
add_source_footnote(fig, "<data source>")
```

Examples: `add_source_footnote(fig, "Bluebikes System Data (bluebikes.com/system-data)")`,
`add_source_footnote(fig, "MTA Turnstile Data via data.ny.gov")`. Avoid vague
placeholders like `"data source"` or `"API"`.

## Tick labels

**Thousands separators** — if a numeric axis's tick labels will show values
in the thousands (or higher), comma-separate them:

```python
from matplotlib.ticker import FuncFormatter

ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
```

**Dates** — never use `YYYY-MM` / `YYYY-MM-DD` style tick labels. Use:
- `"Oct"` (3-letter month abbreviation) when the axis stays within one year
  and the year is unambiguous or shown elsewhere (e.g. in the title).
- `"Oct 2025"` (3-letter month + 4-digit year) when the axis spans multiple
  years, so the year is disambiguated at every tick.

With pandas/matplotlib datetime axes, set this explicitly rather than
relying on `fig.autofmt_xdate()` defaults:

```python
import matplotlib.dates as mdates

ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))       # "Oct"
# or, spanning multiple years:
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))    # "Oct 2025"
```

## Axis labels

Don't add a redundant "Month" or "Date" axis label when the tick labels
already make that self-explanatory (e.g. month abbreviations along the
x-axis). Only label an axis when it adds information the ticks don't
already convey (e.g. "Trips", "Revenue ($)").

## Titles

Never use an em dash (—) or en dash (–) in chart titles (or anywhere else
in chart text). Use a colon, "to", or a plain phrasing instead, e.g.
`"Bluebikes Monthly Ridership, Apr 2025 to Jun 2026"` rather than
`"Bluebikes Monthly Ridership — Apr 2025 to Jun 2026"`.
