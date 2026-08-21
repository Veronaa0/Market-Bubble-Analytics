"""
This is the scoring part - turning the five dimensions into one 0-100 number
per regime so they're actually comparable.

The five dimensions:
  1. valuation_speculation - how stretched valuations/speculation were (my label)
  2. volatility             - how turbulent the regime was (from real VIX data)
  3. market_momentum        - how strong the S&P 500 trend was (from real return data)
  4. ipo_activity           - how hot IPO/speculative issuance was (my label)
  5. macro_liquidity        - how loose money was (from real Fed Funds Rate data)

Three of these come straight from downloaded data now (see
compute_regime_metrics.py) - I only hand-labeled valuation_speculation and
ipo_activity, because I couldn't find a free, trustworthy automated source
for either one in the time I had for Stage 1.

Each label gets mapped to a number on a fixed scale (Low/Tight = 20,
Moderate = 45, High = 70, Loose = 80, Extreme/Very Loose = 95), and the
final score is just the average of the five, weighted equally. Equal
weighting is a simplification, not something I derived - see the README's
Limitations section for more on that. This is just a weighted average, not
a model of any kind, and it isn't trying to predict anything.
"""

import pandas as pd

ORDINAL_SCALE = {
    "low": 20,
    "tight": 20,
    "moderate": 45,
    "high": 70,
    "loose": 80,
    "extreme": 95,
    "very loose": 95,
}

DIMENSION_WEIGHTS = {
    "valuation_speculation": 0.20,
    "volatility": 0.20,
    "market_momentum": 0.20,
    "ipo_activity": 0.20,
    "macro_liquidity": 0.20,
}


def _score_ordinal(label: str) -> float:
    """Map a clean ordinal label (e.g. 'Extreme') to its 0-100 sub-score."""
    key = label.strip().lower()
    if key not in ORDINAL_SCALE:
        raise ValueError(f"Unrecognized ordinal label: '{label}'")
    return ORDINAL_SCALE[key]


def compute_bubble_regime_score(df: pd.DataFrame) -> pd.DataFrame:
    """Add sub-scores and a composite Bubble Regime Score (0-100) to df.

    Assumes df already has the qualitative columns (valuation_speculation,
    ipo_activity) and the data-derived columns (volatility_environment,
    market_momentum, macro_liquidity) merged in - run_analysis.py handles
    that merge before calling this.
    """
    scored = df.copy()

    scored["score_valuation_speculation"] = scored["valuation_speculation"].apply(_score_ordinal)
    scored["score_volatility"] = scored["volatility_environment"].apply(_score_ordinal)
    scored["score_market_momentum"] = scored["market_momentum"].apply(_score_ordinal)
    scored["score_ipo_activity"] = scored["ipo_activity"].apply(_score_ordinal)
    scored["score_macro_liquidity"] = scored["macro_liquidity"].apply(_score_ordinal)

    scored["bubble_regime_score"] = (
        scored["score_valuation_speculation"] * DIMENSION_WEIGHTS["valuation_speculation"]
        + scored["score_volatility"] * DIMENSION_WEIGHTS["volatility"]
        + scored["score_market_momentum"] * DIMENSION_WEIGHTS["market_momentum"]
        + scored["score_ipo_activity"] * DIMENSION_WEIGHTS["ipo_activity"]
        + scored["score_macro_liquidity"] * DIMENSION_WEIGHTS["macro_liquidity"]
    ).round(1)

    return scored


def save_scored_dataset(
    df: pd.DataFrame, output_path: str = "Data/Processed/bubble_regimes_scored.csv"
) -> pd.DataFrame:
    scored = compute_bubble_regime_score(df)
    scored.to_csv(output_path, index=False)
    print(f"Saved scored dataset: {output_path}")
    return scored
