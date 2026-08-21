# Where this data comes from

Last fetched: 2026-08-21

| File | Source | Series | Notes |
|---|---|---|---|
| sp500_daily.csv | Yahoo Finance | ^GSPC daily close | Free, no API key |
| vix_daily.csv | Yahoo Finance | ^VIX daily close | Free, no API key |
| fed_funds_rate_daily.csv | FRED (Federal Reserve Bank of St. Louis) | DFF (Effective Federal Funds Rate) | Free, no API key |

These files get overwritten every time src/fetch_market_data.py runs, so the AI-boom numbers will keep shifting slightly as new trading days happen.
