# Market data sources and Etsy sales integration

## Verified data sources
- **Etsy Marketplace Insights**: direct 30-day Etsy search volume and competition, through the seller UI; no documented public API for this feature. Import manually into `observations.csv` with `source=etsy_insights`. Do not automate scraping.
- **Etsy Open API v3**: own-shop transactions, read-only, with OAuth scope `transactions_r`. Collector obtains an access token through existing `scripts/etsy_api.py` and aggregates orders/units/gross revenue by keyword and currency. No buyer identities retained.
- **Other trend sources**: may be imported as distinct named sources, never relabeled Etsy search volume. Google Trends API remains access-controlled alpha; relative interest is not absolute Etsy searches.

## Local commands
```bash
python -m unittest discover -s market-intelligence -p 'test_*.py' -v
python market-intelligence/scanner.py --observations allowed-insights.csv --output /tmp/niches.json
```

CSV columns: `keyword,source,observed_at,searches,competition,price,trend`. Searches and competition must refer to the SAME keyword, platform and measurement window; do not fill from unrelated public estimate. Price and trend optional. All amounts per transaction from the Etsy API are gross and explicitly EXCLUDE fees. Never use these as net profit.

## Own shop sales (not automatically enabled)
1. Reauthorize Etsy OAuth with `transactions_r`, maintaining existing listing read/write/shop permissions needed by other workflows.
2. Ensure GitHub Actions secrets `ETSY_KEYSTRING`, `ETSY_SHARED_SECRET`, `ETSY_REFRESH_TOKEN` exist and refresh token is updated if rotated.
3. Set `market-intelligence/listing-keywords.csv` with actual `listing_id,keyword` pairs (start from example).
4. After merging approved code, run **Etsy sales read-only analysis** manually. A separate read-only workflow produces aggregate artifacts only; missing scope or mapping makes the run fail safely.

The scanner can also load a sanitized own-sales JSON using `--sales /path/etsy-sales.json`. It NEVER claims this is net earnings. Marketplace competition scanning of other Etsy shops is not enabled. Scheduled jobs on GitHub operate from default branch after merge.
