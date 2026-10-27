# Sounddesk Market Intelligence Scanner

Standalone research module. It does NOT scrape Etsy/eRank, publish products, spend money, or fetch protected demand statistics.

## Inputs
Two optional CSV files, UTF-8 with headers:

- `observations.csv`: `keyword,source,observed_at,searches,competition,price,trend`
- `performance.csv`: `keyword,observed_at,impressions,clicks,orders,revenue,fees`

Dates: ISO YYYY-MM-DD. Use `source=etsy_insights` **only** for matched Etsy Marketplace Insights searches and competition, obtained via permitted manual data export/entry. Other sources remain stored without being treated as Etsy demand. Do not falsify a source. `trend` is a percentage change and can be negative if supplied (currently the importer accepts nonnegative values; leave blank for declines until supported).

## Run
```bash
python market-intelligence/scanner.py --db market-intelligence/data/market.sqlite --observations your-observations.csv --performance your-performance.csv
python -m unittest discover -s market-intelligence -p 'test_*.py' -v
```

Outputs JSON to `market-intelligence/reports/latest.json`, with an explicit `unverified` state for unsupported niches. Reports must not be interpreted as forecasts of sales. Persist your SQLite database externally (or reimport CSV each run): GitHub Actions runners are ephemeral.

## Design notes
- Initial niche score is heuristic, not trained. Real feedback uses orders, CTR, conversion and revenue after fees.
- Fee inputs must include listing/relisting, marketing and processing fees for meaningful margin.
- Do not automatically prune low-impression items; low exposure is not failed demand.
- The scheduled workflow only runs tests plus static candidate reports. No spend, scraping or autonomous account access.
- Before Etsy competitors can be automatically analyzed, obtain API/data-use permission.
- Before full self-learning, add measured performance with exposure controls and A/B testing, and validate the learning process on historical outcomes.
