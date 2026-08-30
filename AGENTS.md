# data-science

A single-Poetry-environment workspace for ad-hoc and repeatable urban /
transportation / open-data analyses: MTA, GTFS, open data portals,
imported CSVs, and similar.

## Environment

One root Poetry environment covers the whole repo — there's no per-analysis
venv.

```bash
poetry install
poetry run python -m ipykernel install --user --name data-science
poetry run nbstripout --install
git config core.hooksPath .githooks
```

Open notebooks with the `data-science` kernel. `shared/` is installed as a
regular importable package, so `import shared.plots.style` (etc.) works from
any notebook regardless of how deeply it's nested — no `sys.path` hacks.

`nbstripout --install` sets up a local git filter (see `.gitattributes`) that
strips notebook outputs/execution counts at `git add` time, before they ever
reach the index — outputs stay visible in your working copy while you run
the notebook, they just never land in a commit. `git config core.hooksPath
.githooks` then points git at the repo's tracked `.githooks/pre-commit`,
which prints a confirmation line per staged notebook at commit time (and
fails the commit if one somehow still has outputs — usually because the
`nbstripout --install` step above was skipped on this clone). Both are
one-time-per-clone, since neither `.git/config` nor the default hooks path
is itself version-controlled.

## Directory contract

```
analyses/
  adhoc/{domain}/{analysis_project_name}/     # e.g. adhoc/mta/fare-evasion
  adhoc/{analysis_project_name}/              # when no natural domain grouping exists
  playbooks/{repeatable_analysis_folder}/     # e.g. playbooks/bluebikes_demand_tracking
```

Inside each `adhoc/...` or `playbooks/...` project folder:

- `data/raw/{data_folder}/{date_or_range}/data.csv|.parquet` — imported files or
  API/portal cache. Never hand-edited. The date/range (or another parameter)
  subfolder is included only when explicitly relevant, not by default.
  For anything fetched (not just imported), the notebook should **load the
  cache if it exists, and only fetch (then write the cache) if it doesn't** —
  see `analyses/adhoc/template_fetch_data/`. Re-running a notebook shouldn't
  re-hit an API/portal for a pull it already has on disk. The exception is
  genuinely live/real-time data (e.g. GTFS-RT), where each pull *is* a new
  snapshot — key those by pull timestamp instead, as
  `analyses/playbooks/inspect_gtfs_rt/` does.
- `data/processed/{data_folder}/data.csv|.parquet` — only things produced
  *from* a notebook or script; nothing goes here by hand.
- `outputs/{date_or_range}/` — reports (`.md`, no subfolder needed), plus
  `tables/` and `charts/` subfolders for anything tabular or visual.
- `AGENTS.md` — short context for the project: what question it answers, not
  implementation detail.
- `analysis.ipynb` if the project answers one question, or
  `analysis_{suffix}.ipynb` per angle if it looks at several.

## Working style

- Default to notebooks, self-contained. Only pull code out into a
  `utils.py` / `plots.py` alongside the notebook once it's grown unwieldy,
  or into a standalone script when a repeatable run is explicitly wanted —
  don't pre-abstract before that's actually true.
- Every plot gets a footnote: `Source: {data_source}`. Use
  `shared.plots.style.add_source_footnote(fig, source)`.
- Call `shared.plots.style.apply_theme()` near the top of a notebook before
  plotting, for consistent fonts/palette/dpi.

## `shared/`

Grows opportunistically as repeated needs show up, not preemptively.
Currently:

- `shared/api.py` — a minimal `get(base_url, path, params, headers)` HTTP
  wrapper. Deliberately thin; expect source-specific variants later.
- `shared/plots/style.py` — `apply_theme()` and `add_source_footnote()`.
- `shared/gtfs_rt.py` + `shared/agencies.yaml` — GTFS-Realtime `.pb` feed
  fetch/parse helpers (see `analyses/playbooks/inspect_gtfs_rt/`).

## Templates

- `analyses/adhoc/template_local_data/` — importing/analyzing a local CSV.
- `analyses/adhoc/template_fetch_data/` — fetching from an open/live API,
  caching the raw pull, and producing a chart.

Copy one of these as the starting point for a new analysis rather than
building from scratch.

## Data hygiene

`data/` and `outputs/` under every analysis are gitignored by default (see
root `.gitignore`) — real and fetched data shouldn't clutter the repo. The
one exception is `template_local_data`'s small synthetic sample CSV, which
is intentionally checked in so that template runs with zero setup.
