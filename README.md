# U.S. Treasury Yield Curve Decomposition (1Y–30Y): Nominal, Real & Breakeven

A live, auto-refreshing [Streamlit](https://streamlit.io) dashboard for the US rates market.
It pulls quotes from CNBC (via the [`ycnbc`](https://pypi.org/project/ycnbc/) package) and displays,
side by side on one page:

| Left | Right |
| --- | --- |
| **Yield Change Curve Comparison** — change vs. previous close for nominal yields, TIPS real yields and inflation breakevens across the 1Y / 2Y / 5Y / 10Y / 30Y tenors | **Current Yield Levels** — the current level of the same three curves |
| Tabular version of the change curve | Tabular version of the current levels |

- **Nominal yields:** US1Y, US2Y, US5Y, US10Y, US30Y
- **Real yields (TIPS):** US1YTIPS, US2YTIPS, US5YTIPS, US10YTIPS, US30YTIPS
- **Breakevens:** nominal − real for each tenor
- Quotes refresh automatically every **30 seconds** (only the dashboard fragment re-runs — the page does not reload).

## Installation

Requires Python 3.10+.

```bash
# clone the repo
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# (recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser. The charts and tables refresh
every 30 seconds for as long as the app is running.

## Notes

- Quotes come from CNBC; outside market hours values may be static, and if the
  CNBC endpoint is briefly unreachable the app shows a warning and retries on
  the next cycle instead of crashing.
- CNBC reports `"UNCH"` for unchanged TIPS quotes — the app treats this as `0.0`
  change (handled by `to_numeric_scalar`).
- **Change vs. original script:** in the original standalone script, the right
  ("Current Yield Levels") chart accidentally plotted the *change* values again.
  This version reads the current-level DataFrames (`nominal_current_df`,
  `real_current_df`, `inflation_breakeven_current_df`) so the right chart shows
  true levels. To reproduce the original behaviour exactly, replace those three
  `.iloc[-1]` reads with the change DataFrames in `fetch_and_compute()`.

## Project structure

```text
├── app.py             # Streamlit app (data fetch + charts + tables)
├── requirements.txt   # Python dependencies
├── README.md
├── LICENSE            # Dual license: MIT (original code) + Apache 2.0 (ycnbc)
└── .gitignore
```

## Licenses

This project uses a **dual-license** structure to accurately reflect the two
distinct categories of intellectual property present when this software is
built and run.

### Original source code — MIT License

All files authored in this repository (`app.py`, `README.md`, and supporting
files) are copyright (c) 2026 and released under the **MIT License**.
See [`LICENSE`](LICENSE) — Part 1 for the full MIT text.

### Third-party dependency — Apache License 2.0

This project depends at runtime on [`ycnbc`](https://pypi.org/project/ycnbc/)
(© 2022 Asep Saputra), which is **not** bundled in this repository and is
**not** covered by the MIT License above. `ycnbc` is distributed separately
under the **Apache License, Version 2.0**.

In accordance with Apache License §4(a), the full Apache 2.0 text is
reproduced in [`LICENSE`](LICENSE) — Part 2, and is also available at:
<http://www.apache.org/licenses/LICENSE-2.0>

> **Disclaimer:** This project is not affiliated with, endorsed by, or vetted
> by CNBC. The `ycnbc` package uses web scraping and is intended for research
> and educational purposes only. All market data retrieved at runtime is
> sourced from CNBC's public endpoints and remains subject to CNBC's own terms
> of service.
