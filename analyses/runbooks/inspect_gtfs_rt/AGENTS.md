# inspect_gtfs_rt

Repeatable playbook for pulling a GTFS-Realtime feed and eyeballing it: a
table of the raw fields plus a map of every vehicle's current position.
Currently wired to MBTA vehicle positions via `shared.gtfs_rt`; add more
agencies in `shared/agencies.yaml` as needed.
