# maag (mobility at a glance)

Prints a one-screen snapshot of the transport options near home:

- next eastbound Green Line (D branch) departures from Brookline Village
- next 66 bus northbound (toward Harvard) from Harvard St @ Aspinwall Ave
  (MBTA stop `1369`)
- Bluebikes availability (classic / e-bikes / docks) at the home stations

Transit times come from MBTA V3 API `/predictions`; bikes from the Bluebikes
GBFS `station_status` feed. Everything is live, so nothing is cached — each
run is a fresh glance. Run with:

```bash
poetry run python analyses/runbooks/maag/maag.py
```
