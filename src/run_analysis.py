"""
Runs the whole Stage 1 pipeline end to end.

    .venv\\Scripts\\python.exe src\\run_analysis.py

Pulls fresh S&P 500 / VIX / Fed Funds Rate data, computes the per-regime
metrics from it, merges that with my valuation/IPO labels, scores each
regime, prints the pandas comparisons, builds the four charts, and writes
reports/findings.md. Needs internet since it re-downloads data every time.
"""

import os
from datetime import date

import pandas as pd

from build_dataset import save_raw_dataset
from bubble_score import save_scored_dataset
from compute_regime_metrics import save_regime_metrics
from fetch_market_data import fetch_and_save_all
from visualize import generate_all_charts

pd.set_option("display.width", 140)
pd.set_option("display.max_colwidth", 40)


def print_section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def build_merged_dataset() -> pd.DataFrame:
    """Combine real market-data metrics with the qualitative regime labels."""
    qualitative = save_raw_dataset()
    metrics = save_regime_metrics()
    merged = qualitative.merge(metrics, on="regime", how="left")
    merged.to_csv("Data/Processed/bubble_regimes_merged.csv", index=False)
    return merged


def analyze(scored: pd.DataFrame) -> pd.DataFrame:
    """Print ranking and dimension comparisons; return the ranked DataFrame."""
    print_section("Real market data by episode")
    print(
        scored[
            [
                "regime",
                "data_window_start",
                "data_window_end",
                "sp500_cumulative_return_pct",
                "sp500_max_drawdown_pct",
                "vix_avg",
                "vix_max",
                "fed_funds_avg",
            ]
        ].to_string(index=False)
    )

    print_section("Bubble Regime Score - ranked highest to lowest")
    ranked = scored.sort_values("bubble_regime_score", ascending=False).reset_index(drop=True)
    ranked.index += 1
    print(ranked[["regime", "peak_year", "bubble_regime_score"]].to_string())

    print_section("Sub-score breakdown by dimension")
    dimension_cols = [
        "regime",
        "score_valuation_speculation",
        "score_volatility",
        "score_market_momentum",
        "score_ipo_activity",
        "score_macro_liquidity",
        "bubble_regime_score",
    ]
    print(scored[dimension_cols].to_string(index=False))

    print_section("Average sub-score across all four regimes (per dimension)")
    dimension_only = dimension_cols[1:-1]
    print(scored[dimension_only].mean().round(1).to_string())

    return ranked


def main() -> None:
    os.makedirs("reports/figures", exist_ok=True)
    os.makedirs("Data/raw", exist_ok=True)
    os.makedirs("Data/Processed", exist_ok=True)

    print_section("Fetching real market data (Yahoo Finance + FRED)")
    fetch_and_save_all()

    merged = build_merged_dataset()
    scored = save_scored_dataset(merged)
    ranked = analyze(scored)
    generate_all_charts(scored)

    write_findings_report(ranked)
    print_section("Done")
    print("Findings written to reports/findings.md")
    print("Charts written to reports/figures/")


def write_findings_report(ranked: pd.DataFrame) -> None:
    ai = ranked[ranked["regime"] == "Current AI boom"].iloc[0]
    ai_rank = int(ranked.index[ranked["regime"] == "Current AI boom"][0])
    top = ranked.iloc[0]
    gfc = ranked[ranked["regime"] == "US housing / Global Financial Crisis"].iloc[0]
    fetch_date = date.today().isoformat()

    lines = []
    lines.append("# Stage 1 findings\n")
    lines.append(
        f"Numbers below are from a run on {fetch_date}. Volatility, momentum, and "
        f"macro liquidity come straight out of downloaded S&P 500 / VIX data (Yahoo "
        f"Finance) and the Fed Funds Rate (FRED) - I didn't touch those numbers by "
        f"hand. Valuation/speculation and IPO activity are still my own call, since "
        f"I couldn't find a free source for either that I trusted enough to automate "
        f"in the time I had. Full writeup of how the score works is in the README.\n"
    )

    lines.append("## Market data, by episode\n")
    lines.append("| Regime | Window | S&P 500 return | Max drawdown | Avg VIX | Peak VIX | Avg Fed Funds Rate |")
    lines.append("|---|---|---|---|---|---|---|")
    for _, row in ranked.iterrows():
        lines.append(
            f"| {row['regime']} | {row['data_window_start']} to {row['data_window_end']} "
            f"| {row['sp500_cumulative_return_pct']:+.1f}% | {row['sp500_max_drawdown_pct']:.1f}% "
            f"| {row['vix_avg']:.1f} | {row['vix_max']:.1f} | {row['fed_funds_avg']:.2f}% |"
        )
    lines.append("")

    lines.append("## Bubble Regime Score, ranked\n")
    lines.append("| Rank | Regime | Peak year | Score |")
    lines.append("|---|---|---|---|")
    for i, row in ranked.iterrows():
        lines.append(f"| {i} | {row['regime']} | {row['peak_year']} | {row['bubble_regime_score']} |")
    lines.append("")

    lines.append("## What stood out\n")
    tied_at_top = ranked[ranked["bubble_regime_score"] == top["bubble_regime_score"]]
    if len(tied_at_top) > 1:
        names = " and ".join(tied_at_top["regime"].tolist())
        lines.append(
            f"{names} tied for the top score ({top['bubble_regime_score']}), which "
            f"tracks with how both are usually described - extreme on valuation and "
            f"IPO activity, with the real VIX data backing that up."
        )
    else:
        lines.append(
            f"{top['regime']} came out on top ({top['bubble_regime_score']}), which "
            f"tracks with how it's usually described - extreme on both valuation and "
            f"IPO activity, and the real VIX data backs that up too."
        )
    lines.append("")
    lines.append(
        f"The Global Financial Crisis is the odd one out. It has the worst real "
        f"drawdown of the four ({gfc['sp500_max_drawdown_pct']:.1f}%) and the "
        f"highest peak VIX ({gfc['vix_max']:.1f}), but it lands in the middle of "
        f"the ranking. That's because most of the excess in 2003-2009 was in "
        f"mortgage credit, not stock valuations or IPOs, and those are the two "
        f"dimensions this score leans on most."
    )
    lines.append("")
    lines.append(
        f"The current AI boom is the one I was most curious about, and it actually "
        f"scored lowest ({ai['bubble_regime_score']}, rank {ai_rank} of {len(ranked)}). "
        f"Not what I expected going in. Its S&P 500 return "
        f"({ai['sp500_cumulative_return_pct']:+.1f}% since {ai['data_window_start']}) "
        f"is the strongest of any regime here, but average VIX ({ai['vix_avg']:.1f}) "
        f"is the lowest, and the Fed Funds Rate is nowhere near the near-zero levels "
        f"seen in 2003-2007 or 2020-2021 (it's averaged {ai['fed_funds_avg']:.2f}% so "
        f"far). So by the numbers this run has been calmer and less rate-fueled than "
        f"the past three, even with the strong returns."
    )
    lines.append("")

    lines.append("## On the AI boom specifically\n")
    lines.append(
        "I want to be upfront about this part: it's the least settled section of "
        "the whole project, because the regime itself isn't over. The end date in "
        "the table above is just today's date, not a real endpoint, so these "
        "numbers will keep moving every time I rerun this.\n"
    )
    lines.append(
        "What I can say is that the AI boom looks like past booms in some ways "
        "(strong momentum concentrated in a handful of companies) and different in "
        "others (real interest rates staying high instead of near zero, valuation "
        "labeled 'High' rather than 'Extreme' in my own judgment). I'm not trying "
        "to predict a crash here, and this score isn't a forecast of anything - it's "
        "just a way to line the AI boom up against past episodes on the same scale "
        "and see where it agrees or disagrees with them.\n"
    )

    lines.append("## Limitations\n")
    lines.append(
        "- Valuation/speculation and IPO activity are still my own labels, not "
        "pulled data. See src/build_dataset.py for exactly what I mean by that.\n"
        "- All five dimensions are weighted equally (20% each) because I don't "
        "have a good basis for weighting them differently yet - not because equal "
        "weighting is obviously correct.\n"
        "- The start/end year for each regime is a judgment call on my part, not a "
        "hard boundary anyone would agree on exactly.\n"
        "- The AI boom numbers are a moving target by definition, since that regime "
        "hasn't ended.\n"
        "- Four data points is not a sample size you can run statistics on, so I "
        "haven't tried to.\n"
    )

    with open("reports/findings.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
