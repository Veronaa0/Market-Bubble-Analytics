# Stage 1 findings

Numbers below are from a run on 2026-08-21. Volatility, momentum, and macro liquidity come straight out of downloaded S&P 500 / VIX data (Yahoo Finance) and the Fed Funds Rate (FRED) - I didn't touch those numbers by hand. Valuation/speculation and IPO activity are still my own call, since I couldn't find a free source for either that I trusted enough to automate in the time I had. Full writeup of how the score works is in the README.

## Market data, by episode

| Regime | Window | S&P 500 return | Max drawdown | Avg VIX | Peak VIX | Avg Fed Funds Rate |
|---|---|---|---|---|---|---|
| Dot-com bubble | 1995-01-03 to 2002-12-31 | +91.6% | -49.1% | 22.2 | 45.7 | 4.84% |
| 2020-2022 speculative boom | 2020-01-02 to 2022-12-30 | +17.9% | -33.9% | 24.8 | 82.7 | 0.71% |
| US housing / Global Financial Crisis | 2003-01-02 to 2009-12-31 | +22.7% | -56.8% | 20.7 | 80.9 | 2.54% |
| Current AI boom | 2023-01-03 to 2026-08-20 | +99.8% | -18.9% | 17.4 | 52.3 | 4.59% |

## Bubble Regime Score, ranked

| Rank | Regime | Peak year | Score |
|---|---|---|---|
| 1 | Dot-com bubble | 2000 | 80.0 |
| 2 | 2020-2022 speculative boom | 2021 | 80.0 |
| 3 | US housing / Global Financial Crisis | 2007 | 62.0 |
| 4 | Current AI boom | Ongoing (not yet determined) | 60.0 |

## What stood out

Dot-com bubble and 2020-2022 speculative boom tied for the top score (80.0), which tracks with how both are usually described - extreme on valuation and IPO activity, with the real VIX data backing that up.

The Global Financial Crisis is the odd one out. It has the worst real drawdown of the four (-56.8%) and the highest peak VIX (80.9), but it lands in the middle of the ranking. That's because most of the excess in 2003-2009 was in mortgage credit, not stock valuations or IPOs, and those are the two dimensions this score leans on most.

The current AI boom is the one I was most curious about, and it actually scored lowest (60.0, rank 4 of 4). Not what I expected going in. Its S&P 500 return (+99.8% since 2023-01-03) is the strongest of any regime here, but average VIX (17.4) is the lowest, and the Fed Funds Rate is nowhere near the near-zero levels seen in 2003-2007 or 2020-2021 (it's averaged 4.59% so far). So by the numbers this run has been calmer and less rate-fueled than the past three, even with the strong returns.

## On the AI boom specifically

I want to be upfront about this part: it's the least settled section of the whole project, because the regime itself isn't over. The end date in the table above is just today's date, not a real endpoint, so these numbers will keep moving every time I rerun this.

What I can say is that the AI boom looks like past booms in some ways (strong momentum concentrated in a handful of companies) and different in others (real interest rates staying high instead of near zero, valuation labeled 'High' rather than 'Extreme' in my own judgment). I'm not trying to predict a crash here, and this score isn't a forecast of anything - it's just a way to line the AI boom up against past episodes on the same scale and see where it agrees or disagrees with them.

## Limitations

- Valuation/speculation and IPO activity are still my own labels, not pulled data. See src/build_dataset.py for exactly what I mean by that.
- All five dimensions are weighted equally (20% each) because I don't have a good basis for weighting them differently yet - not because equal weighting is obviously correct.
- The start/end year for each regime is a judgment call on my part, not a hard boundary anyone would agree on exactly.
- The AI boom numbers are a moving target by definition, since that regime hasn't ended.
- Four data points is not a sample size you can run statistics on, so I haven't tried to.
