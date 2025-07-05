"""Revenue simulation and back-testing utilities for RL pricing."""
from __future__ import annotations

from typing import List, Dict

import numpy as np
import pandas as pd

from .rl_agent import recommend_price


def simulate_period(
    baseline_price: float,
    demand_series: List[float],
    penalty: float = 0.0,
) -> pd.DataFrame:
    """Simulate revenue over demand_series using RL vs static price.

    Args:
        baseline_price: the fixed price used by the baseline strategy.
        demand_series: list of forecasted demand values.
        penalty: additional per-unit cost for price changes.

    Returns:
        DataFrame with columns: day, demand, baseline_revenue, rl_price,
        rl_revenue, revenue_lift_pct
    """

    records = []
    last_multiplier = 1.0
    for day, demand in enumerate(demand_series, start=1):
        rl_res = recommend_price(demand_forecast=demand, last_multiplier=last_multiplier, base_price=baseline_price)
        rl_price = rl_res["optimal_price"]
        last_multiplier = rl_res["multiplier"]

        baseline_revenue = baseline_price * demand
        rl_revenue = rl_price * demand - penalty * abs(rl_price - baseline_price)
        lift_pct = (rl_revenue - baseline_revenue) / baseline_revenue * 100.0

        records.append(
            {
                "day": day,
                "demand": demand,
                "baseline_price": baseline_price,
                "baseline_revenue": baseline_revenue,
                "rl_price": rl_price,
                "rl_revenue": rl_revenue,
                "revenue_lift_pct": lift_pct,
            }
        )

    return pd.DataFrame.from_records(records)
