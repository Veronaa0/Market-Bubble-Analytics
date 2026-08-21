"""
Pulls real historical data instead of me typing numbers in from memory:

  - S&P 500 daily close  -> Yahoo Finance, ticker "^GSPC"
  - VIX daily close      -> Yahoo Finance, ticker "^VIX"
  - Effective Fed Funds Rate -> FRED, series "DFF"

Both are free, no API key needed. Everything gets saved to Data/raw/ so
there's always a local copy of exactly what got downloaded and when.

Since this re-downloads live data every run, numbers for the still-ongoing
AI boom regime will drift a little run to run as new trading days show up.
That's expected - it's the tradeoff for using live data over a fixed snapshot.
"""

from datetime import date

import pandas as pd
import yfinance as yf

FRED_FED_FUNDS_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF"

START_DATE = "1994-11-01"  # comfortably before the earliest regime (1995)


def fetch_sp500(start: str = START_DATE, end: str | None = None) -> pd.DataFrame:
    """Daily S&P 500 closing price from Yahoo Finance (ticker ^GSPC)."""
    df = yf.Ticker("^GSPC").history(start=start, end=end)[["Close"]]
    df.index = df.index.tz_localize(None).normalize()
    df.index.name = "date"
    df = df.rename(columns={"Close": "sp500_close"})
    return df


def fetch_vix(start: str = START_DATE, end: str | None = None) -> pd.DataFrame:
    """Daily VIX closing level from Yahoo Finance (ticker ^VIX)."""
    df = yf.Ticker("^VIX").history(start=start, end=end)[["Close"]]
    df.index = df.index.tz_localize(None).normalize()
    df.index.name = "date"
    df = df.rename(columns={"Close": "vix_close"})
    return df


def fetch_fed_funds_rate() -> pd.DataFrame:
    """Daily effective Federal Funds Rate from FRED (series DFF)."""
    df = pd.read_csv(FRED_FED_FUNDS_URL)
    df.columns = ["date", "fed_funds_rate"]
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    df["fed_funds_rate"] = pd.to_numeric(df["fed_funds_rate"], errors="coerce")
    return df


def fetch_and_save_all(output_dir: str = "Data/raw") -> None:
    today = date.today().isoformat()

    sp500 = fetch_sp500()
    sp500.to_csv(f"{output_dir}/sp500_daily.csv")
    print(f"Saved {len(sp500)} rows: {output_dir}/sp500_daily.csv (Yahoo Finance ^GSPC, fetched {today})")

    vix = fetch_vix()
    vix.to_csv(f"{output_dir}/vix_daily.csv")
    print(f"Saved {len(vix)} rows: {output_dir}/vix_daily.csv (Yahoo Finance ^VIX, fetched {today})")

    fed_funds = fetch_fed_funds_rate()
    fed_funds = fed_funds[fed_funds.index >= START_DATE]
    fed_funds.to_csv(f"{output_dir}/fed_funds_rate_daily.csv")
    print(f"Saved {len(fed_funds)} rows: {output_dir}/fed_funds_rate_daily.csv (FRED series DFF, fetched {today})")

    with open(f"{output_dir}/data_sources.md", "w", encoding="utf-8") as f:
        f.write(
            "# Where this data comes from\n\n"
            f"Last fetched: {today}\n\n"
            "| File | Source | Series | Notes |\n"
            "|---|---|---|---|\n"
            "| sp500_daily.csv | Yahoo Finance | ^GSPC daily close | Free, no API key |\n"
            "| vix_daily.csv | Yahoo Finance | ^VIX daily close | Free, no API key |\n"
            "| fed_funds_rate_daily.csv | FRED (Federal Reserve Bank of St. Louis) | DFF (Effective Federal Funds Rate) | Free, no API key |\n\n"
            "These files get overwritten every time src/fetch_market_data.py runs, "
            "so the AI-boom numbers will keep shifting slightly as new trading days "
            "happen.\n"
        )


if __name__ == "__main__":
    fetch_and_save_all()
