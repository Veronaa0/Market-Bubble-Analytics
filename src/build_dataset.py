"""
This is the part of the dataset I couldn't automate: which years count as
each regime, the historical narrative (catalyst/unwind/outcome), and two
judgment calls I had to make myself - valuation_speculation and
ipo_activity. I looked for a free, reliable source for both and didn't find
one I trusted enough to wire up in Stage 1, so they're labeled here by hand.

Everything I *could* pull real numbers for - S&P 500 performance, VIX,
Fed Funds Rate - lives in fetch_market_data.py and
compute_regime_metrics.py instead. run_analysis.py merges the two.

COLUMN_SOURCES below just tags each column as either "researcher_label" (my
own ordinal judgment - someone else might label it differently, that's the
point of flagging it) or "researcher_note" (plain historical context, no
number attached to it).
"""

import pandas as pd

REGIMES = [
    {
        "regime": "Dot-com bubble",
        "start_year": 1995,
        "end_year": 2002,
        "peak_year": "2000",
        "valuation_speculation": "Extreme",
        "valuation_speculation_note": "Widespread triple-digit P/E ratios and profitless '.com' companies reaching multi-billion-dollar valuations",
        "ipo_activity": "Extreme",
        "ipo_activity_note": "Record number of tech IPOs in 1999-2000, many more than doubling on their first trading day",
        "major_catalyst": "Commercialization of the internet; huge influx of retail and VC capital into unprofitable '.com' startups",
        "major_unwind": "Nasdaq crash 2000-2002; wave of dot-com bankruptcies",
        "outcome": "Deep sector-specific crash; broader economy entered a mild recession",
    },
    {
        "regime": "US housing / Global Financial Crisis",
        "start_year": 2003,
        "end_year": 2009,
        "peak_year": "2007",
        "valuation_speculation": "High",
        "valuation_speculation_note": "Speculation concentrated in housing prices and mortgage credit rather than public equity valuations broadly",
        "ipo_activity": "Moderate",
        "ipo_activity_note": "IPO market was unremarkable relative to dot-com and 2021; the excess was in mortgage lending and securitization, not equity issuance",
        "major_catalyst": "Subprime mortgage lending, securitization (MBS/CDOs), and excessive leverage in the financial system",
        "major_unwind": "2008 financial crisis; Lehman Brothers collapse; global credit freeze",
        "outcome": "Global recession; large-scale bank bailouts and monetary/fiscal stimulus",
    },
    {
        "regime": "2020-2022 speculative boom",
        "start_year": 2020,
        "end_year": 2022,
        "peak_year": "2021",
        "valuation_speculation": "Extreme",
        "valuation_speculation_note": "Meme-stock mania, SPAC boom, crypto speculation, and rich valuations on unprofitable tech",
        "ipo_activity": "Extreme",
        "ipo_activity_note": "Record SPAC and traditional IPO issuance in 2021",
        "major_catalyst": "COVID-era stimulus, near-zero rates, retail trading boom, SPAC mania",
        "major_unwind": "2022 rate-hiking cycle; sharp declines in unprofitable tech, crypto, and SPACs",
        "outcome": "Broad market correction; many speculative names fell 70-90% from peak",
    },
    {
        "regime": "Current AI boom",
        "start_year": 2023,
        "end_year": 2026,
        "peak_year": "Ongoing (not yet determined)",
        "valuation_speculation": "High",
        "valuation_speculation_note": "Elevated valuations concentrated in AI infrastructure and mega-cap tech; not (yet) as broad-based as dot-com or 2021",
        "ipo_activity": "Moderate",
        "ipo_activity_note": "IPO market has been reopening gradually with some high-profile AI-adjacent listings, but well below 2021 or dot-com peak levels",
        "major_catalyst": "Generative AI breakthroughs (e.g. large language models), massive AI infrastructure/capex spending",
        "major_unwind": "Not applicable yet — regime is ongoing as of this project",
        "outcome": "Unresolved / ongoing — this project draws NO conclusion about a future outcome",
    },
]

COLUMN_SOURCES = {
    "regime": "researcher_label",
    "start_year": "researcher_label",
    "end_year": "researcher_label",
    "peak_year": "researcher_label",
    "valuation_speculation": "researcher_label",
    "valuation_speculation_note": "researcher_note",
    "ipo_activity": "researcher_label",
    "ipo_activity_note": "researcher_note",
    "major_catalyst": "researcher_note",
    "major_unwind": "researcher_note",
    "outcome": "researcher_note",
}


def build_regime_dataframe() -> pd.DataFrame:
    """Return the four-regime qualitative dataset as a pandas DataFrame."""
    return pd.DataFrame(REGIMES)


def save_raw_dataset(output_path: str = "Data/raw/bubble_regimes_qualitative.csv") -> pd.DataFrame:
    """Build the qualitative dataset and write it to Data/raw/."""
    df = build_regime_dataframe()
    df.to_csv(output_path, index=False)
    print(f"Saved qualitative dataset: {output_path}  ({len(df)} regimes, {len(df.columns)} columns)")
    return df


if __name__ == "__main__":
    save_raw_dataset()
