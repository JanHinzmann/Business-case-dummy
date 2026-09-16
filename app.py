"""Streamlit interface for the small-business case calculator."""

from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from business_case import BusinessCaseInputs, calculate_business_case, validate_inputs


st.set_page_config(
    page_title="Business Case Calculator",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px;}
        [data-testid="stMetric"] {
            background: linear-gradient(145deg, #ffffff 0%, #f7f9fc 100%);
            border: 1px solid #e5eaf1;
            border-radius: 0.75rem;
            padding: 0.9rem 1rem;
        }
        .executive-summary {
            border-left: 5px solid #2463eb;
            background: #f5f8ff;
            border-radius: 0.4rem;
            padding: 1rem 1.2rem;
            margin: 0.7rem 0 1.2rem 0;
        }
        .small-note {color: #5d6675; font-size: 0.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


CURRENCIES = {
    "EUR (€)": ("€", "EUR"),
    "USD ($)": ("$", "USD"),
    "GBP (£)": ("£", "GBP"),
}


def format_money(value: float, symbol: str) -> str:
    sign = "−" if value < 0 else ""
    return f"{sign}{symbol}{abs(value):,.0f}"


def format_ratio(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.2f}×"


def format_percent(value: float | None) -> str:
    return "N/A" if value is None else f"{value:,.1f}%"


def format_payback(value: float | None) -> str:
    if value is None:
        return "Not reached"
    if value == 0:
        return "Immediate"
    return f"{value:.2f} years"


with st.sidebar:
    st.header("Assumptions")
    initiative_name = st.text_input(
        "Initiative name",
        value="Digital workflow upgrade",
        help="A short name used in the executive summary and export filename.",
    )
    currency_label = st.selectbox("Currency", list(CURRENCIES))
    currency_symbol, currency_code = CURRENCIES[currency_label]

    st.subheader("Investment and returns")
    initial_investment = st.number_input(
        "One-time initial investment",
        min_value=0.0,
        value=75000.0,
        step=5000.0,
        format="%.2f",
    )
    annual_benefit = st.number_input(
        "Expected annual financial benefit",
        min_value=0.0,
        value=50000.0,
        step=5000.0,
        format="%.2f",
    )
    annual_operating_cost = st.number_input(
        "Annual operating cost",
        min_value=0.0,
        value=12000.0,
        step=1000.0,
        format="%.2f",
    )

    st.subheader("Time and rates")
    analysis_years = st.number_input(
        "Analysis period (years)",
        min_value=1,
        max_value=50,
        value=5,
        step=1,
    )
    discount_rate_percent = st.number_input(
        "Discount rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=8.0,
        step=0.5,
        format="%.2f",
        help="Used to convert future cash flows into today's value.",
    )
    use_growth = st.checkbox("Apply annual benefit growth", value=False)
    benefit_growth_percent = st.number_input(
        "Annual benefit growth (%)",
        min_value=-99.0,
        max_value=100.0,
        value=3.0 if use_growth else 0.0,
        step=0.5,
        format="%.2f",
        disabled=not use_growth,
    )


inputs = BusinessCaseInputs(
    initial_investment=float(initial_investment),
    annual_benefit=float(annual_benefit),
    annual_operating_cost=float(annual_operating_cost),
    analysis_years=int(analysis_years),
    discount_rate=float(discount_rate_percent) / 100,
    benefit_growth_rate=(float(benefit_growth_percent) / 100) if use_growth else 0.0,
)

st.title("Business Case Calculator")
st.caption("Turn a few assumptions into a clear, decision-ready financial view.")

errors = validate_inputs(inputs)
if not initiative_name.strip():
    errors.append("Enter an initiative name before exporting the analysis.")

if errors:
    for error in errors:
        st.error(error)
    st.stop()

if inputs.annual_benefit < inputs.annual_operating_cost:
    st.warning(
        "Annual operating cost is higher than the first-year benefit. "
        "Payback may require strong benefit growth or may not occur within the analysis period."
    )
elif inputs.annual_benefit == 0:
    st.warning("Annual benefit is zero, so the case cannot generate a positive return.")

if inputs.discount_rate > 0.30:
    st.info("The discount rate is unusually high; confirm that it reflects your decision context.")
if inputs.benefit_growth_rate > 0.25:
    st.info("Benefit growth above 25% is ambitious; consider testing a more conservative case.")
if inputs.initial_investment == 0:
    st.info("With no initial investment, payback is immediate and ROI may be undefined if all costs are zero.")

results = calculate_business_case(inputs)

payback_text = format_payback(results.payback_period)
if results.npv > 0:
    recommendation = "creates value on the entered assumptions"
    outlook = "Positive"
elif results.npv < 0:
    recommendation = "does not recover its risk-adjusted cost on the entered assumptions"
    outlook = "Caution"
else:
    recommendation = "is financially neutral on the entered assumptions"
    outlook = "Neutral"

roi_text = format_percent(results.roi_percent)
summary_payback = (
    f"with estimated payback in {results.payback_period:.2f} years"
    if results.payback_period is not None
    else f"without reaching payback inside the {inputs.analysis_years}-year horizon"
)

st.subheader(f"Executive summary · {initiative_name.strip()}")
st.markdown(
    f"""
    <div class="executive-summary">
      <strong>{outlook} outlook.</strong> The initiative {recommendation}, producing an NPV of
      <strong>{format_money(results.npv, currency_symbol)}</strong> and an ROI of
      <strong>{roi_text}</strong> {summary_payback}.
    </div>
    """,
    unsafe_allow_html=True,
)

metric_row_1 = st.columns(4)
metric_row_1[0].metric("Net annual benefit", format_money(results.net_annual_benefit, currency_symbol))
metric_row_1[1].metric("NPV", format_money(results.npv, currency_symbol))
metric_row_1[2].metric("ROI", roi_text)
metric_row_1[3].metric("Payback", payback_text)

metric_row_2 = st.columns(4)
metric_row_2[0].metric("Total benefits", format_money(results.total_benefits, currency_symbol))
metric_row_2[1].metric("Total costs", format_money(results.total_costs, currency_symbol))
metric_row_2[2].metric("Benefit-cost ratio", format_ratio(results.benefit_cost_ratio))
metric_row_2[3].metric(
    "Break-even year",
    str(results.break_even_year) if results.break_even_year is not None else "Not reached",
)

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("Cash-flow outlook")

cash_flow_df = pd.DataFrame(results.cash_flows).rename(
    columns={
        "year": "Year",
        "benefit": "Benefits",
        "operating_cost": "Operating costs",
        "initial_investment": "Initial investment",
        "total_cost": "Total costs",
        "net_cash_flow": "Net cash flow",
        "discounted_cash_flow": "Discounted cash flow",
        "cumulative_cash_flow": "Cumulative cash flow",
        "cumulative_discounted_cash_flow": "Cumulative discounted cash flow",
    }
)

chart_df = cash_flow_df.set_index("Year")[["Net cash flow", "Cumulative cash flow"]]
st.line_chart(chart_df, height=360)
st.caption(
    "Year 0 contains the initial investment. Benefits and operating costs are assumed "
    "to occur at the end of each subsequent year."
)

with st.expander("View yearly cash-flow table", expanded=True):
    visible_columns = [
        "Year",
        "Benefits",
        "Operating costs",
        "Initial investment",
        "Total costs",
        "Net cash flow",
        "Discounted cash flow",
        "Cumulative cash flow",
    ]
    money_columns = visible_columns[1:]
    styled_table = cash_flow_df[visible_columns].style.format(
        {column: lambda value, s=currency_symbol: f"{s}{value:,.2f}" for column in money_columns}
    )
    st.dataframe(styled_table, width="stretch", hide_index=True)

csv_data = cash_flow_df.to_csv(index=False).encode("utf-8")
safe_name = re.sub(r"[^a-z0-9]+", "-", initiative_name.lower()).strip("-") or "business-case"
st.download_button(
    "Download yearly results as CSV",
    data=csv_data,
    file_name=f"{safe_name}-{currency_code.lower()}.csv",
    mime="text/csv",
)

with st.expander("How the figures are calculated"):
    st.markdown(
        f"""
        - **Net annual benefit** is the first-year benefit minus annual operating cost.
        - **ROI** is total undiscounted net value divided by total undiscounted costs over {inputs.analysis_years} years.
        - **NPV** discounts each year-end net cash flow at {discount_rate_percent:.2f}% and includes the year-zero investment.
        - **Benefit-cost ratio** divides discounted benefits by discounted investment and operating costs.
        - **Payback** uses undiscounted cash flow and estimates the fraction of the break-even year needed to recover the remaining investment.
        - Benefit growth, when enabled, compounds annually; operating cost remains flat.
        """
    )

st.divider()
st.markdown(
    '<p class="small-note">This calculator provides estimates based solely on the assumptions entered. '
    "It is not financial advice; validate material decisions against your organization's finance and risk standards.</p>",
    unsafe_allow_html=True,
)
