# bluebikes/gbfs

Pulls the latest `station_information` and `station_status` feeds from the
[Bluebikes GBFS](https://gbfs.bluebikes.com/gbfs/gbfs.json) (feed URLs
discovered from `gbfs.json`) and caches each as
`data/raw/{feed_name}/{pulled_at}/data.csv`, where `pulled_at` is the UTC
pull timestamp (`YYYY-MM-DDTHHMMSSZ`). GBFS is live, so every run writes a
new snapshot rather than reading from cache.
