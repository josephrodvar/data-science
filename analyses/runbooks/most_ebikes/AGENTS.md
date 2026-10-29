# most_ebikes

Where are the most e-bikes right now? Pulls a live snapshot of the
[Bluebikes GBFS](https://gbfs.bluebikes.com/gbfs/gbfs.json)
`station_information` and `station_status` feeds (cached by UTC pull
timestamp, like `runbooks/bluebikes/gbfs/`), joins them on `station_id`, and
ranks stations two ways:

- top 5 by e-bikes as a share of total docks (`num_ebikes_available / capacity`),
  limited to stations with at least `MIN_CAPACITY` docks so tiny stations
  don't hit 100% on one bike;
- top 5 by raw e-bike count.

Charts and tables go to `outputs/{pulled_at}/`.
