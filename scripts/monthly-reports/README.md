# Monthly reports page

Interactive archive of the monthly threat reports in [`rootlist/`](../../rootlist/):
monthly and cumulative charts, daily activity, top registrars and domain zones,
VirusTotal coverage, a CSV export and searchable records for every month.

Live page: https://phishdestroy.github.io/destroylist/scripts/monthly-reports/

## How it updates

`build_data.py` reads every `rootlist/YYYY/MM/YYYY-MM-threats.json` and writes
`data/index.json`, `data/YYYY.json` and `data/YYYY-MM-indicators.json`.
The Pages workflow runs it before every deploy (every 3 hours and on changes
under `scripts/`), so new monthly reports appear on the page without any manual
step. The `data/` directory is generated and not committed.

Links: `?year=2026&month=07` opens a specific month.
