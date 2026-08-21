"""
Four charts, saved as PNGs to reports/figures/. Two of them (VIX and market
performance) plot the real downloaded numbers in their own units - VIX
points, % return - instead of the 0-100 scores, since actual numbers are
more convincing than a normalized score. Just matplotlib, nothing fancy.
"""

import matplotlib.pyplot as plt
import pandas as pd

# Consistent regime -> color mapping so the same episode always reads the
# same color across every chart in the report.
REGIME_COLORS = {
    "Dot-com bubble": "#4C72B0",
    "US housing / Global Financial Crisis": "#C44E52",
    "2020-2022 speculative boom": "#DD8452",
    "Current AI boom": "#55A868",
}

FIGURE_SIZE = (8, 5)
DPI = 150


def _bar_colors(regimes: pd.Series) -> list:
    return [REGIME_COLORS.get(r, "#888888") for r in regimes]


def plot_bubble_regime_scores(df: pd.DataFrame, output_path: str) -> None:
    """Bar chart: composite Bubble Regime Score by episode, ranked highest to lowest."""
    ranked = df.sort_values("bubble_regime_score", ascending=False)

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    bars = ax.bar(ranked["regime"], ranked["bubble_regime_score"], color=_bar_colors(ranked["regime"]))
    ax.bar_label(bars, fmt="%.0f", padding=3)

    ax.set_title("Bubble Regime Score by Episode", fontsize=13, fontweight="bold")
    ax.set_ylabel("Bubble Regime Score (0-100)")
    ax.set_ylim(0, 105)
    ax.set_xticks(range(len(ranked)))
    ax.set_xticklabels(ranked["regime"], rotation=15, ha="right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=DPI)
    plt.close(fig)
    print(f"Saved chart: {output_path}")


def plot_vix_comparison(df: pd.DataFrame, output_path: str) -> None:
    """Bar chart: real average VIX level by episode (actual VIX points, from Yahoo Finance)."""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    bars = ax.bar(df["regime"], df["vix_avg"], color=_bar_colors(df["regime"]))
    ax.bar_label(bars, fmt="%.1f", padding=3)

    ax.set_title("Average VIX Level by Episode\n(real data, Yahoo Finance ^VIX daily close)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Average VIX (index points)")
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df["regime"], rotation=15, ha="right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    ax.axhline(20, color="gray", linestyle="--", linewidth=1, alpha=0.6)
    ax.text(len(df) - 0.5, 20.5, "long-run VIX average ≈ 20", fontsize=8, color="gray", ha="right")

    fig.tight_layout()
    fig.savefig(output_path, dpi=DPI)
    plt.close(fig)
    print(f"Saved chart: {output_path}")


def plot_market_performance(df: pd.DataFrame, output_path: str) -> None:
    """Grouped bar chart: real S&P 500 cumulative return vs. max drawdown by episode."""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    x = range(len(df))
    width = 0.35

    bars1 = ax.bar(
        [i - width / 2 for i in x], df["sp500_cumulative_return_pct"], width,
        label="Cumulative return over window", color="#55A868",
    )
    bars2 = ax.bar(
        [i + width / 2 for i in x], df["sp500_max_drawdown_pct"], width,
        label="Max drawdown within window", color="#C44E52",
    )
    ax.bar_label(bars1, fmt="%.0f%%", padding=3, fontsize=8)
    ax.bar_label(bars2, fmt="%.0f%%", padding=3, fontsize=8)

    ax.set_title("S&P 500 Performance by Episode\n(real data, Yahoo Finance ^GSPC daily close)", fontsize=12, fontweight="bold")
    ax.set_ylabel("% change")
    ax.set_xticks(list(x))
    ax.set_xticklabels(df["regime"], rotation=15, ha="right")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(output_path, dpi=DPI)
    plt.close(fig)
    print(f"Saved chart: {output_path}")


def plot_dimension_radar(df: pd.DataFrame, output_path: str) -> None:
    """Radar chart comparing all four regimes across the five scoring dimensions."""
    dimensions = [
        ("score_valuation_speculation", "Valuation /\nSpeculation"),
        ("score_volatility", "Volatility"),
        ("score_market_momentum", "Market\nMomentum"),
        ("score_ipo_activity", "IPO\nActivity"),
        ("score_macro_liquidity", "Macro\nLiquidity"),
    ]
    labels = [label for _, label in dimensions]
    cols = [col for col, _ in dimensions]

    num_vars = len(cols)
    angles = [n / float(num_vars) * 2 * 3.141592653589793 for n in range(num_vars)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8.5), subplot_kw=dict(polar=True))

    for _, row in df.iterrows():
        values = [row[col] for col in cols]
        values += values[:1]
        color = REGIME_COLORS.get(row["regime"], "#888888")
        ax.plot(angles, values, color=color, linewidth=2, label=row["regime"])
        ax.fill(angles, values, color=color, alpha=0.08)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_title("Regime Comparison Across Scoring Dimensions", fontsize=13, fontweight="bold", pad=30)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, fontsize=8)

    fig.tight_layout()
    fig.savefig(output_path, dpi=DPI)
    plt.close(fig)
    print(f"Saved chart: {output_path}")


def generate_all_charts(scored_df: pd.DataFrame, output_dir: str = "reports/figures") -> None:
    plot_bubble_regime_scores(scored_df, f"{output_dir}/bubble_regime_scores.png")
    plot_vix_comparison(scored_df, f"{output_dir}/vix_comparison.png")
    plot_market_performance(scored_df, f"{output_dir}/market_performance.png")
    plot_dimension_radar(scored_df, f"{output_dir}/dimension_radar.png")


if __name__ == "__main__":
    scored = pd.read_csv("Data/Processed/bubble_regimes_scored.csv")
    generate_all_charts(scored)
