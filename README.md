# Market Bubble Analytics

A small project comparing historical speculative market episodes with the current AI boom, using real downloaded market data plus a couple of labels I assigned myself where I couldn't find good free data.

**Status: Stage 1.** This is a first pass, not a finished research system. I'm being upfront about what's real data and what's my own judgment call throughout - see [Limitations](#limitations) for the honest version of what this can and can't do.

## The question I'm trying to answer

How did major speculative market episodes differ in terms of performance, volatility, valuation, and broader conditions - and can that comparison say anything useful about where the current AI boom stands relative to them?

## Why I built this

People compare booms informally all the time ("is this the new dot-com?") without much of a consistent basis for the comparison. I wanted to build the smallest version of that basis that I could trust: real historical data for four episodes, one simple scoring method applied the same way to all of them, and a few charts that actually show what's going on rather than just asserting it.

## The four regimes

| Regime | Roughly | Peaked |
|---|---|---|
| Dot-com bubble | 1995–2002 | 2000 |
| US housing / Global Financial Crisis | 2003–2009 | 2007 |
| 2020–2022 speculative boom | 2020–2022 | 2021 |
| Current AI boom | 2023–present | still ongoing |

I picked these year ranges myself based on how these periods are generally described - they're not exact boundaries anyone would agree on down to the month.

## How it works

### 1. Pulling real data ([`src/fetch_market_data.py`](src/fetch_market_data.py))

Every time I run the analysis, it downloads fresh:

- S&P 500 daily closing price (Yahoo Finance, ticker `^GSPC`)
- VIX daily closing level (Yahoo Finance, ticker `^VIX`)
- Effective Federal Funds Rate (FRED, series `DFF`)

Both sources are free and don't need an API key. Raw downloads land in `Data/raw/`, along with `data_sources.md` recording exactly what was pulled and when.

### 2. Turning that into per-regime numbers ([`src/compute_regime_metrics.py`](src/compute_regime_metrics.py))

For each regime's date window I calculate, directly from the downloaded data:

- S&P 500 cumulative return and max drawdown (worst peak-to-trough decline) over the window
- average and peak VIX over the window
- average Fed Funds Rate over the window

Then I bucket those into Low/Moderate/High/Extreme using fixed cutoffs I set ahead of time (e.g. average VIX under 15 is "Low," over 30 is "Extreme") - the same rule applied to every regime, not tuned after the fact.

### 3. The two things I couldn't automate ([`src/build_dataset.py`](src/build_dataset.py))

I looked for a free, reliable source for valuation multiples and IPO issuance volume and didn't find one I trusted enough to wire up in the time I had, so these two stay as my own labels:

- **valuation/speculation** - how stretched valuations and speculative behavior were
- **IPO activity** - how hot new-issuance was

Someone else could reasonably label these differently. I'm flagging that rather than pretending it's a measurement. Everything else in the qualitative file (which years, the catalyst/unwind/outcome narrative) is standard, well-documented history rather than an opinion of mine.

### 4. The Bubble Regime Score ([`src/bubble_score.py`](src/bubble_score.py))

Five dimensions, weighted equally at 20% each:

| Dimension | Where it comes from |
|---|---|
| Valuation / speculation | my label |
| Volatility | real - from average VIX |
| Market momentum | real - from S&P 500 return |
| IPO activity | my label |
| Macro liquidity | real - from average Fed Funds Rate |

Each label maps to a number (Low/Tight → 20, Moderate → 45, High → 70, Loose → 80, Extreme/Very Loose → 95), and the score is just the average of the five. That's it - it's a weighted average, not a model, and it isn't trying to predict anything. It exists so the four regimes can sit on the same 0–100 scale for comparison.

### 5. Analysis ([`src/run_analysis.py`](src/run_analysis.py))

Merges the real metrics with my labels, ranks the regimes, breaks each one down by dimension, and prints the pandas tables to the console. Also writes everything to [`reports/findings.md`](reports/findings.md), including the actual underlying numbers so you can trace any score back to what produced it.

### 6. Charts ([`src/visualize.py`](src/visualize.py))

Four PNGs, saved to `reports/figures/`:

1. Bubble Regime Score by episode
2. Average VIX by episode (real numbers, actual index points)
3. S&P 500 return vs. max drawdown by episode (real numbers, actual %)
4. Radar chart comparing all five dimensions across all four regimes

## Where the data actually comes from

- S&P 500 and VIX: Yahoo Finance, via the `yfinance` library. Free, no key.
- Fed Funds Rate: FRED, via their public CSV endpoint. Free, no key.
- Valuation/speculation, IPO activity, and the historical narrative: me, based on general financial history that's well documented elsewhere. Not pulled from any live source, and I've said so wherever it matters.

Because the data refreshes on every run, the numbers for the still-ongoing AI boom (and anything touching recent dates) will shift a bit between runs. That's expected - it's the cost of using live data instead of a frozen snapshot.

## What I found

(This section summarizes [`reports/findings.md`](reports/findings.md), which gets regenerated with exact numbers and the fetch date every time the script runs.)

The 2020-2022 boom and the dot-com bubble score highest - both got "Extreme" on my valuation/IPO labels, and the real volatility and rate data backs that up. The Global Financial Crisis has the worst real drawdown and the highest peak VIX of the four, but lands in the middle of the ranking, because its excess was in mortgage credit rather than stock valuations or IPOs, which is what this score weighs most heavily.

The current AI boom actually came out lowest, which surprised me a little going in. Its S&P 500 return is the strongest of the four, but its average VIX is the lowest and the Fed Funds Rate has stayed well above the near-zero levels of the prior two booms. So by these particular measures, this run has been calmer and less rate-driven than the ones before it, even with strong returns.

### On the AI boom specifically

This part is the least settled, because the regime isn't over. I want to be clear that I'm not predicting anything here - the score isn't a crash forecast, and I have no idea when or how this ends. What I can say is that it shares some traits with past booms (strong, narrow momentum) and differs in others (tighter interest rates than any prior boom in this dataset). That's the extent of the claim.

## Limitations

- valuation_speculation and ipo_activity are my labels, not data. See `src/build_dataset.py`.
- All five dimensions are weighted equally because I don't have a good basis for weighting them differently yet, not because equal weighting is obviously correct.
- Regime years are my own approximation of when each episode started and ended.
- The VIX/Fed-Funds bucket cutoffs are fixed thresholds I chose, not something derived statistically.
- The AI boom numbers are a moving target since that regime hasn't ended - they'll be different next time this runs.
- Four data points isn't a sample size you can run statistics on, so I haven't tried to.

## What I'd want to add next

Stage 1 is deliberately small. Things I'd want to build if I keep going:

- A real valuation series (like the Shiller CAPE ratio) to replace my manual valuation label
- Actual IPO issuance data to replace my manual IPO activity label
- Company-level case studies within each regime
- Looking at individual speculative stocks (SPCE and similar) alongside the index-level view
- More macro variables - credit spreads, money supply, employment
- Actual statistical testing of differences between regimes, once there's more than four data points to work with
- Some kind of validation of the score against real outcomes, possibly ML-based
- Comparing this framework against future IPOs of major private tech companies as they go public

None of that is built yet. Stage 1 is: real market data, real per-regime metrics computed from it, two labeled judgment calls, a score, the pandas comparisons, four charts, and this writeup.

## Running it

```bash
# from the project root, with the existing .venv already set up
.venv\Scripts\pip.exe install matplotlib yfinance   # one-time, if not already installed
.venv\Scripts\python.exe src\run_analysis.py
```

Needs an internet connection since it re-downloads market data every run. This regenerates everything under `Data/raw/`, `Data/Processed/`, `reports/figures/`, and `reports/findings.md`.

## Project layout

```text
Market Bubble Analytics/
├── Data/
│   ├── raw/                        # downloaded data + my qualitative labels
│   │   ├── sp500_daily.csv          # Yahoo Finance ^GSPC
│   │   ├── vix_daily.csv            # Yahoo Finance ^VIX
│   │   ├── fed_funds_rate_daily.csv # FRED DFF
│   │   ├── data_sources.md          # what got fetched, and when
│   │   └── bubble_regimes_qualitative.csv
│   └── Processed/
│       ├── regime_market_metrics.csv  # real per-regime metrics
│       ├── bubble_regimes_merged.csv  # real metrics + my labels
│       └── bubble_regimes_scored.csv  # + the computed score
├── Notebooks/                # scratch/exploration
├── src/
│   ├── fetch_market_data.py     # downloads S&P 500 / VIX / Fed Funds Rate
│   ├── compute_regime_metrics.py # turns that into per-regime numbers
│   ├── build_dataset.py         # the two labels I assigned + the narrative
│   ├── bubble_score.py          # the scoring math
│   ├── visualize.py             # the four charts
│   └── run_analysis.py          # runs everything end to end
├── reports/
│   ├── figures/               # the generated charts
│   └── findings.md            # generated findings writeup
├── models/                    # empty for now, future ML/stats work
├── dashboards/                # empty for now, future interactive dashboard
└── README.md
```
