"""Financial calculations for the Streamlit business-case app."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BusinessCaseInputs:
    initial_investment: float
    annual_benefit: float
    annual_operating_cost: float
    analysis_years: int
    discount_rate: float
    benefit_growth_rate: float = 0.0


@dataclass(frozen=True)
class BusinessCaseResults:
    cash_flows: list[dict[str, float | int]]
    net_annual_benefit: float
    total_benefits: float
    total_costs: float
    roi_percent: float | None
    npv: float
    benefit_cost_ratio: float | None
    payback_period: float | None
    break_even_year: int | None


def validate_inputs(inputs: BusinessCaseInputs) -> list[str]:
    """Return human-readable validation errors without raising UI-specific errors."""
    errors: list[str] = []
    if inputs.initial_investment < 0:
        errors.append("Initial investment cannot be negative.")
    if inputs.annual_benefit < 0:
        errors.append("Annual financial benefit cannot be negative.")
    if inputs.annual_operating_cost < 0:
        errors.append("Annual operating cost cannot be negative.")
    if isinstance(inputs.analysis_years, bool) or not isinstance(inputs.analysis_years, int):
        errors.append("Analysis period must be a whole number of years.")
    elif inputs.analysis_years < 1:
        errors.append("Analysis period must be at least one year.")
    if inputs.discount_rate <= -1:
        errors.append("Discount rate must be greater than -100%.")
    if inputs.benefit_growth_rate <= -1:
        errors.append("Benefit growth rate must be greater than -100%.")
    return errors


def calculate_business_case(inputs: BusinessCaseInputs) -> BusinessCaseResults:
    """Calculate annual cash flows and conventional business-case metrics.

    Rates are decimals (for example, 0.08 means 8%). Benefits and operating
    costs occur at each year end; the initial investment occurs in year zero.
    """
    errors = validate_inputs(inputs)
    if errors:
        raise ValueError(" ".join(errors))

    cash_flows: list[dict[str, float | int]] = []
    cumulative_cash_flow = -float(inputs.initial_investment)
    cumulative_discounted_cash_flow = cumulative_cash_flow
    cash_flows.append(
        {
            "year": 0,
            "benefit": 0.0,
            "operating_cost": 0.0,
            "initial_investment": float(inputs.initial_investment),
            "total_cost": float(inputs.initial_investment),
            "net_cash_flow": -float(inputs.initial_investment),
            "discounted_cash_flow": -float(inputs.initial_investment),
            "cumulative_cash_flow": cumulative_cash_flow,
            "cumulative_discounted_cash_flow": cumulative_discounted_cash_flow,
        }
    )

    total_benefits = 0.0
    total_operating_costs = 0.0
    discounted_benefits = 0.0
    discounted_costs = float(inputs.initial_investment)
    payback_period: float | None = 0.0 if inputs.initial_investment == 0 else None
    break_even_year: int | None = 0 if inputs.initial_investment == 0 else None

    for year in range(1, inputs.analysis_years + 1):
        benefit = float(inputs.annual_benefit) * (
            (1 + inputs.benefit_growth_rate) ** (year - 1)
        )
        operating_cost = float(inputs.annual_operating_cost)
        net_cash_flow = benefit - operating_cost
        discount_factor = (1 + inputs.discount_rate) ** year
        discounted_cash_flow = net_cash_flow / discount_factor

        previous_cumulative = cumulative_cash_flow
        cumulative_cash_flow += net_cash_flow
        cumulative_discounted_cash_flow += discounted_cash_flow

        total_benefits += benefit
        total_operating_costs += operating_cost
        discounted_benefits += benefit / discount_factor
        discounted_costs += operating_cost / discount_factor

        if payback_period is None and previous_cumulative < 0 <= cumulative_cash_flow:
            if net_cash_flow > 0:
                payback_period = (year - 1) + (-previous_cumulative / net_cash_flow)
                break_even_year = year

        cash_flows.append(
            {
                "year": year,
                "benefit": benefit,
                "operating_cost": operating_cost,
                "initial_investment": 0.0,
                "total_cost": operating_cost,
                "net_cash_flow": net_cash_flow,
                "discounted_cash_flow": discounted_cash_flow,
                "cumulative_cash_flow": cumulative_cash_flow,
                "cumulative_discounted_cash_flow": cumulative_discounted_cash_flow,
            }
        )

    total_costs = float(inputs.initial_investment) + total_operating_costs
    net_value = total_benefits - total_costs
    roi_percent = (net_value / total_costs * 100) if total_costs else None
    benefit_cost_ratio = (
        discounted_benefits / discounted_costs if discounted_costs else None
    )

    return BusinessCaseResults(
        cash_flows=cash_flows,
        net_annual_benefit=float(inputs.annual_benefit)
        - float(inputs.annual_operating_cost),
        total_benefits=total_benefits,
        total_costs=total_costs,
        roi_percent=roi_percent,
        npv=cumulative_discounted_cash_flow,
        benefit_cost_ratio=benefit_cost_ratio,
        payback_period=payback_period,
        break_even_year=break_even_year,
    )
