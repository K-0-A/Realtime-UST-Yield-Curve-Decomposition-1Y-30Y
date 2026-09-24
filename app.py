"""
Realtime US Treasury Yield Curve Decomposition (1Y-30Y) (Streamlit)

Auto-refreshing dashboard showing:
  - US nominal Treasury yields (US1Y, US2Y, US5Y, US10Y, US30Y)
  - US TIPS real yields (US1YTIPS ... US30YTIPS)
  - Inflation breakevens (nominal - real)
as two side-by-side charts (change curve + current levels) with the
matching data tables underneath. Data source: CNBC via the `ycnbc` package.

Run with:  streamlit run app.py

-------------------------------------------------------------------------------
Third-Party Attribution
-------------------------------------------------------------------------------
This file uses the `ycnbc` package (https://pypi.org/project/ycnbc/) to
retrieve market data from CNBC's public endpoints at runtime.

  ycnbc — Copyright 2022 Asep Saputra
  Licensed under the Apache License, Version 2.0
  https://github.com/codestorm-official/ycnbc

The Apache License, Version 2.0 is reproduced in full in the LICENSE file
distributed with this repository (Part 2), and is also available at:
  http://www.apache.org/licenses/LICENSE-2.0

`ycnbc` is not affiliated with, endorsed by, or vetted by CNBC. It is an
open-source tool that uses web scraping and is intended for research and
educational purposes only.
-------------------------------------------------------------------------------
"""

import streamlit as st
import pandas as pd
import numpy as np
import ycnbc as CNBC
import matplotlib.pyplot as plt
import seaborn as ss


# ---------------------------------------------------------------------------
# Original script logic, preserved in full and wrapped in a function so
# Streamlit can re-run it on every refresh cycle.
# ---------------------------------------------------------------------------

def to_numeric_scalar(x):
    # handle dicts containing ticker -> Series/scalar
    if isinstance(x, dict):
        v = next(iter(x.values()))
        return to_numeric_scalar(v)

    # pandas Series or numpy array -> take first element
    if isinstance(x, (pd.Series, np.ndarray)):
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x[0])

    # handle string tokens like 'UNCH' -> treat as 0.0
    if isinstance(x, str):
        if x.strip().upper() == 'UNCH':
            return 0.0

    return float(x)  # scalar already


def fetch_and_compute():
    """Pull fresh quotes from CNBC and build the two plotting DataFrames.

    Returns (df_plot, df_current, fig) or raises on data errors.
    """

    # calling the real yields tips
    markets = CNBC.Markets()

    tips_1 = markets.quote_summary('US1YTIPS')
    tips_2 = markets.quote_summary('US2YTIPS')
    tips_5 = markets.quote_summary('US5YTIPS')
    tips_10 = markets.quote_summary('US10YTIPS')
    tips_30 = markets.quote_summary('US30YTIPS')

    # calling the current price of real yields
    current_tips_yield_1 = tips_1.get('last')
    current_tips_yield_2 = tips_2.get('last')
    current_tips_yield_5 = tips_5.get('last')
    current_tips_yield_10 = tips_10.get('last')
    current_tips_yield_30 = tips_30.get('last')

    # calling the change in real yields
    current_change_tips_1 = tips_1.get('change')
    current_change_tips_2 = tips_2.get('change')
    current_change_tips_5 = tips_5.get('change')
    current_change_tips_10 = tips_10.get('change')
    current_change_tips_30 = tips_30.get('change')

    # calling the nominal yields
    current_yield_1 = markets.quote_summary('US1Y')
    current_yield_2 = markets.quote_summary('US2Y')
    current_yield_5 = markets.quote_summary('US5Y')
    current_yield_10 = markets.quote_summary('US10Y')
    current_yield_30 = markets.quote_summary('US30Y')

    # calling the current price of nominal yields
    current_last_yield_1 = current_yield_1.get('last')
    current_last_yield_2 = current_yield_2.get('last')
    current_last_yield_5 = current_yield_5.get('last')
    current_last_yield_10 = current_yield_10.get('last')
    current_last_yield_30 = current_yield_30.get('last')

    # calling the change in nominal yields
    current_change_yield_1 = current_yield_1.get('change')
    current_change_yield_2 = current_yield_2.get('change')
    current_change_yield_5 = current_yield_5.get('change')
    current_change_yield_10 = current_yield_10.get('change')
    current_change_yield_30 = current_yield_30.get('change')

    # remove '%' and convert to decimal
    val = current_tips_yield_10 if current_tips_yield_10 is not None else '0%'
    if isinstance(val, (int, float)):
        # assume numeric is expressed in percent (e.g. 1.23 for 1.23%)
        numeric_yield = float(val)
    else:
        numeric_yield = float(str(val).strip().rstrip('%'))

    # remove '%' and convert to decimal on the current price of yields
    convert_last_yield_1 = float(str(current_last_yield_1).strip().rstrip('%'))
    convert_last_yield_2 = float(str(current_last_yield_2).strip().rstrip('%'))
    convert_last_yield_5 = float(str(current_last_yield_5).strip().rstrip('%'))
    convert_last_yield_10 = float(str(current_last_yield_10).strip().rstrip('%'))
    convert_last_yield_30 = float(str(current_last_yield_30).strip().rstrip('%'))

    # remove '%' and convert to decimal on the current price of real yields
    convert_last_tips_1 = float(str(current_tips_yield_1).strip().rstrip('%'))
    convert_last_tips_2 = float(str(current_tips_yield_2).strip().rstrip('%'))
    convert_last_tips_5 = float(str(current_tips_yield_5).strip().rstrip('%'))
    convert_last_tips_10 = float(str(current_tips_yield_10).strip().rstrip('%'))
    convert_last_tips_30 = float(str(current_tips_yield_30).strip().rstrip('%'))

    # Convert to pandas Series for easy calculation yields on the last price
    close_last_yield_1year = pd.Series(convert_last_yield_1, index=['US1Y'])
    close_last_yield_2year = pd.Series(convert_last_yield_2, index=['US2Y'])
    close_last_yield_5year = pd.Series(convert_last_yield_5, index=['US5Y'])
    close_last_yield_10year = pd.Series(convert_last_yield_10, index=['US10Y'])
    close_last_yield_30year = pd.Series(convert_last_yield_30, index=['US30Y'])

    # Convert to pandas Series for easy calculation yields on the change
    close_change_yield_1year = pd.Series(current_change_yield_1, index=['US1Y'])
    close_change_yield_2year = pd.Series(current_change_yield_2, index=['US2Y'])
    close_change_yield_5year = pd.Series(current_change_yield_5, index=['US5Y'])
    close_change_yield_10year = pd.Series(current_change_yield_10, index=['US10Y'])
    close_change_yield_30year = pd.Series(current_change_yield_30, index=['US30Y'])

    # Convert to pandas Series for easy calculation real yields on the last price
    close_last_tips_1year = pd.Series(convert_last_tips_1, index=['US1YTIPS'])
    close_last_tips_2year = pd.Series(convert_last_tips_2, index=['US2YTIPS'])
    close_last_tips_5year = pd.Series(convert_last_tips_5, index=['US5YTIPS'])
    close_last_tips_10year = pd.Series(convert_last_tips_10, index=['US10YTIPS'])
    close_last_tips_30year = pd.Series(convert_last_tips_30, index=['US30YTIPS'])

    # Convert to pandas Series for easy calculation real yields on the change
    close_change_tips_1year = pd.Series(current_change_tips_1, index=['US1YTIPS'])
    close_change_tips_2year = pd.Series(current_change_tips_2, index=['US2YTIPS'])
    close_change_tips_5year = pd.Series(current_change_tips_5, index=['US5YTIPS'])
    close_change_tips_10year = pd.Series(current_change_tips_10, index=['US10YTIPS'])
    close_change_tips_30year = pd.Series(current_change_tips_30, index=['US30YTIPS'])

    # convert current price in yields to numeric series
    close_last_yields_1year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_last_yield_1year.items()})
    close_last_yields_2year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_last_yield_2year.items()})
    close_last_yields_5year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_last_yield_5year.items()})
    close_last_yields_10year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_last_yield_10year.items()})
    close_last_yields_30year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_last_yield_30year.items()})

    # convert change in yields to numeric series
    close_change_yield_1year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_change_yield_1year.items()})
    close_change_yield_2year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_change_yield_2year.items()})
    close_change_yield_5year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_change_yield_5year.items()})
    close_change_yield_10year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_change_yield_10year.items()})
    close_change_yield_30year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_change_yield_30year.items()})

    # convert current price in real yields to numeric series
    close_last_tips_1year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_last_tips_1year.items()})
    close_last_tips_2year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_last_tips_2year.items()})
    close_last_tips_5year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_last_tips_5year.items()})
    close_last_tips_10year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_last_tips_10year.items()})
    close_last_tips_30year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_last_tips_30year.items()})

    # convert change in real yields to numeric series
    close_change_tips_1year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_change_tips_1year.items()})
    close_change_tips_2year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_change_tips_2year.items()})
    close_change_tips_5year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_change_tips_5year.items()})
    close_change_tips_10year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_change_tips_10year.items()})
    close_change_tips_30year_num = pd.Series({idx: to_numeric_scalar(v) for idx, v in close_change_tips_30year.items()})

    # calculating the inflation breakeven by subtracting each equivalent real yield from nominal yields
    Current_inflation_breakeven_1year = close_last_yields_1year_num.values - (close_last_tips_1year_num.values)
    Current_inflation_breakeven_2year = close_last_yields_2year_num.values - (close_last_tips_2year_num.values)
    Current_inflation_breakeven_5year = close_last_yields_5year_num.values - (close_last_tips_5year_num.values)
    Current_inflation_breakeven_10year = close_last_yields_10year_num.values - (close_last_tips_10year_num.values)
    Current_inflation_breakeven_30year = close_last_yields_30year_num.values - (close_last_tips_30year_num.values)

    # calculating the inflation breakeven change by subtracting each equivalent real yield from nominal yield
    inflation_breakeven_1year = close_change_yield_1year_num.values - (close_change_tips_1year_num.values)
    inflation_breakeven_2year = close_change_yield_2year_num.values - (close_change_tips_2year_num.values)
    inflation_breakeven_5year = close_change_yield_5year_num.values - (close_change_tips_5year_num.values)
    inflation_breakeven_10year = close_change_yield_10year_num.values - (close_change_tips_10year_num.values)
    inflation_breakeven_30year = close_change_yield_30year_num.values - (close_change_tips_30year_num.values)

    # putting the respective categories under one dataframe for plotting on the left chart
    change_in_nominal_yields_df = pd.DataFrame({'1nyr': close_change_yield_1year_num.values,
                                                '2nyr': close_change_yield_2year_num.values,
                                                '5nyr': close_change_yield_5year_num.values,
                                                '10nyr': close_change_yield_10year_num.values,
                                                '30nyr': close_change_yield_30year_num.values
                                                })

    change_in_real_yields_df = pd.DataFrame({'1ryr': close_change_tips_1year_num.values,
                                             '2ryr': close_change_tips_2year_num.values,
                                             '5ryr': close_change_tips_5year_num.values,
                                             '10ryr': close_change_tips_10year_num.values,
                                             '30ryr': close_change_tips_30year_num.values
                                             })

    change_in_inflation_breakeven_df = pd.DataFrame({'1iyr': inflation_breakeven_1year,
                                                     '2iyr': inflation_breakeven_2year,
                                                     '5iyr': inflation_breakeven_5year,
                                                     '10iyr': inflation_breakeven_10year,
                                                     '30iyr': inflation_breakeven_30year
                                                     })

    # Create a combined DataFrame with tenors as rows for x axis
    tenors = [1, 2, 5, 10, 30]

    data = {
        'Tenor': tenors,
        'Nominal': change_in_nominal_yields_df.iloc[-1].tolist(),
        'Real': change_in_real_yields_df.iloc[-1].tolist(),
        'Breakeven': change_in_inflation_breakeven_df.iloc[-1].tolist()
    }

    df_plot = pd.DataFrame(data)

    # Melt to long format for seaborn
    df_long = df_plot.melt(id_vars='Tenor',
                           var_name='Category',
                           value_name='Value')

    # right chart for the current levels of nominal, real, and breakeven yields
    nominal_current_df = pd.DataFrame({
        '1nyr': close_last_yields_1year_num.values,
        '2nyr': close_last_yields_2year_num.values,
        '5nyr': close_last_yields_5year_num.values,
        '10nyr': close_last_yields_10year_num.values,
        '30nyr': close_last_yields_30year_num.values
    })

    real_current_df = pd.DataFrame({
        '1ryr': close_last_tips_1year_num.values,
        '2ryr': close_last_tips_2year_num.values,
        '5ryr': close_last_tips_5year_num.values,
        '10ryr': close_last_tips_10year_num.values,
        '30ryr': close_last_tips_30year_num.values
    })

    inflation_breakeven_current_df = pd.DataFrame({
        '1iyr': Current_inflation_breakeven_1year,
        '2iyr': Current_inflation_breakeven_2year,
        '5iyr': Current_inflation_breakeven_5year,
        '10iyr': Current_inflation_breakeven_10year,
        '30iyr': Current_inflation_breakeven_30year
    })

    # Extract the most recent values for current levels
    # (fixed: read from the *current-level* DataFrames so the right chart
    #  shows actual yield levels, not the daily changes)
    nominal_current = nominal_current_df.iloc[-1].tolist()
    real_current = real_current_df.iloc[-1].tolist()
    breakeven_current = inflation_breakeven_current_df.iloc[-1].tolist()

    # Build DataFrame for right chart
    df_current = pd.DataFrame({
        'Tenor': tenors,
        'Nominal': nominal_current,
        'Real': real_current,
        'Breakeven': breakeven_current
    })

    # Melt to long format
    df_current_long = df_current.melt(id_vars='Tenor', var_name='Category', value_name='Value')

    # 4. Build the two charts as separate figures so each can occupy its own
    #    Streamlit column (still displayed side by side, as in the original).
    palette = {'Nominal': 'green', 'Real': 'red', 'Breakeven': 'orange'}

    # 5. Left chart: Yield Change Curve Comparison
    fig_change, ax1 = plt.subplots(figsize=(7, 6))
    ss.lineplot(data=df_long,
                x='Tenor',
                y='Value',
                hue='Category',
                palette=palette,
                marker='o',
                linewidth=2.5, ax=ax1)

    ax1.set_title('Current Yield Change from Previous close: Nominal, Real, and Breakeven', fontsize=14)
    ax1.set_xlabel('Tenor (years)', fontsize=12)
    ax1.set_ylabel('Percent', fontsize=14)
    ax1.legend(title='Category')
    ax1.grid(True, linestyle='--', alpha=0.7)
    fig_change.tight_layout()

    # Right chart: Current levels
    fig_levels, ax2 = plt.subplots(figsize=(7, 6))
    ss.lineplot(data=df_current_long,
                x='Tenor', y='Value', hue='Category',
                palette=palette,
                marker='o', linewidth=2.5, ax=ax2)

    ax2.set_title('Current Yield Levels: Nominal, Real, and Breakeven', fontsize=14)
    ax2.set_xlabel('Tenor (years)')
    ax2.set_ylabel('Percent', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend(title='Category')
    fig_levels.tight_layout()

    return df_plot, df_current, fig_change, fig_levels


# ---------------------------------------------------------------------------
# Streamlit page
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Realtime US Treasury Yield Curve Decomposition (1Y-30Y)", layout="wide")


@st.fragment(run_every=30)
def dashboard():
    """Auto-refreshes every 30 seconds without reloading the whole page."""
    st.caption(f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} — refreshes every 30 seconds")

    try:
        df_plot, df_current, fig_change, fig_levels = fetch_and_compute()
    except Exception as e:  # CNBC unreachable, market closed, missing quote, etc.
        st.warning(f"Could not refresh quotes ({e}). Retrying on the next cycle…")
        return

    # Row 1 — charts side by side
    chart_left, chart_right = st.columns(2)
    with chart_left:
        st.subheader("Current Yield Change from Previous close: Nominal, Real, and Breakeven")
        st.pyplot(fig_change)
        plt.close(fig_change)
    with chart_right:
        st.subheader("Current Yield Levels: Nominal, Real, and Breakeven")
        st.pyplot(fig_levels)
        plt.close(fig_levels)

    # Row 2 — tables side by side
    table_left, table_right = st.columns(2)
    with table_left:
        st.subheader("Current Yield Change from Previous close (%)")
        st.dataframe(df_plot, use_container_width=True, hide_index=True)
    with table_right:
        st.subheader("Current Yield Levels (%)")
        st.dataframe(df_current, use_container_width=True, hide_index=True)


def main():
    st.title("Realtime US Treasury Yield Curve Decomposition (1Y-30Y)")
    st.markdown(
        "Live US Treasury **nominal** yields, **TIPS ** yields and "
        "**inflation breakevens** — change vs. previous close and current levels."
    )
    dashboard()


if __name__ == "__main__":
    main()
