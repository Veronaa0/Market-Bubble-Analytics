"""
Takes the raw S&P 500 / VIX / Fed Funds Rate history that fetch_market_data.py
downloads and, for each regime's date window, works out:

  - sp500_cumulative_return_pct : % change in the S&P 500 from the first to
                                   the last trading day in the window
  - sp500_max_drawdown_pct      : worst peak-to-trough decline within the window
  - vix_avg / vix_max           : average and peak VIX during the window
  - fed_funds_avg               : average Fed Funds Rate during the window

None of these four are hand-typed - they're calculated straight from the
downloaded data. The regime windows (which years count as which bubble) are
still my own call though.

I then bucket those raw numbers into the same Low/Moderate/High/Extreme
labels the rest of the project uses, using fixed thresholds I picked ahead
of time (not tuned after seeing which regime it would flatter). Those
buckets feed into bubble_score.py.
"""

from datetime import date

import pandas as pd

# Regime windows: (start_year, end_year). end_year for the ongoing AI boom
# is capped at "today" when slicing data, not a fixed future date.
REGIME_WINDOWS = {
    "Dot-com bubble": (1995, 2002),
    "US housing / Global Financial Crisis": (2003, 2009),
    "2020-2022 speculative boom": (2020, 2022),
    "Current AI boom": (2023, date.today().year),
}


def _window_slice(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    start = f"{start_year}-01-01"
    end = min(f"{end_year}-12-31", date.today().isoformat())
    return df.loc[start:end]


def _max_drawdown_pct(prices: pd.Series) -> float:
    """Largest peak-to-trough % decline within the given price series."""
    running_max = prices.cummax()
    drawdown = (prices / running_max - 1) * 100
    return round(drawdown.min(), 1)


def _bucket_vix(avg_vix: float) -> str:
    """Volatility label from average VIX, using commonly-cited VIX bands
    (long-run VIX average is roughly 19-20; >30 is widely treated as a
    crisis/panic level)."""
    if avg_vix < 15:
        return "Low"
    if avg_vix < 20:
        return "Moderate"
    if avg_vix < 30:
        return "High"
    return "Extreme"


def _bucket_fed_funds(avg_rate: float) -> str:
    """Macro liquidity label from the average Fed Funds Rate: a lower rate
    means cheaper borrowing / looser liquidity conditions."""
    if avg_rate < 1.0:
        return "Very Loose"
    if avg_rate < 3.0:
        return "Loose"
    if avg_rate < 5.0:
        return "Moderate"
    return "Tight"


def _bucket_momentum(cumulative_return_pct: float) -> str:
    """Momentum label from cumulative S&P 500 return over the window."""
    if cumulative_return_pct >= 60:
        return "Extreme"
    if cumulative_return_pct >= 30:
        return "High"
    if cumulative_return_pct >= 10:
        return "Moderate"
    return "Low"


def compute_all_regime_metrics(
    sp500: pd.DataFrame, vix: pd.DataFrame, fed_funds: pd.DataFrame
) -> pd.DataFrame:
    rows = []
    for regime, (start_year, end_year) in REGIME_WINDOWS.items():
        sp_window = _window_slice(sp500, start_year, end_year)["sp500_close"]
        vix_window = _window_slice(vix, start_year, end_year)["vix_close"]
        rate_window = _window_slice(fed_funds, start_year, end_year)["fed_funds_rate"]

        cumulative_return = round((sp_window.iloc[-1] / sp_window.iloc[0] - 1) * 100, 1)
        max_drawdown = _max_drawdown_pct(sp_window)
        vix_avg = round(vix_window.mean(), 1)
        vix_max = round(vix_window.max(), 1)
        fed_funds_avg = round(rate_window.mean(), 2)

        rows.append(
            {
                "regime": regime,
                "data_window_start": sp_window.index.min().date().isoformat(),
                "data_window_end": sp_window.index.max().date().isoformat(),
                "sp500_cumulative_return_pct": cumulative_return,
                "sp500_max_drawdown_pct": max_drawdown,
                "vix_avg": vix_avg,
                "vix_max": vix_max,
                "fed_funds_avg": fed_funds_avg,
                "volatility_environment": _bucket_vix(vix_avg),
                "macro_liquidity": _bucket_fed_funds(fed_funds_avg),
                "market_momentum": _bucket_momentum(cumulative_return),
            }
        )

    return pd.DataFrame(rows)


def save_regime_metrics(output_path: str = "Data/Processed/regime_market_metrics.csv") -> pd.DataFrame:
    sp500 = pd.read_csv("Data/raw/sp500_daily.csv", index_col="date", parse_dates=True)
    vix = pd.read_csv("Data/raw/vix_daily.csv", index_col="date", parse_dates=True)
    fed_funds = pd.read_csv("Data/raw/fed_funds_rate_daily.csv", index_col="date", parse_dates=True)

    metrics = compute_all_regime_metrics(sp500, vix, fed_funds)
    metrics.to_csv(output_path, index=False)
    print(f"Saved regime metrics: {output_path}")
    return metrics


if __name__ == "__main__":
    save_regime_metrics()
