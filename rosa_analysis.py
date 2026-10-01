"""Shared, reproducible calculations for Rosa's four-week simulator.

The professor's starter package remains unchanged. The notebook includes these
same function definitions so its single-file submission can run independently.
"""

import math
from numbers import Real

import numpy as np
import pandas as pd
from starter import ZONES, TIME_BLOCKS, COSTS, PROMISE, delivery_times

SEED = 1


def positive_number(value, name):
    """Reject nonnumeric, infinite, or nonpositive inputs."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a positive finite number.")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number.")
    return float(value)


def validate_costs(costs):
    """Return validated refund, future-order loss, and margin assumptions."""
    checked = {}
    for key in ("refund", "churn_orders", "margin"):
        if key not in costs:
            raise ValueError(f"Missing cost assumption: {key}.")
        value = costs[key]
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError(f"{key} must be a finite nonnegative number.")
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{key} must be a finite nonnegative number.")
        checked[key] = float(value)
    return checked


def selected_times(zone, time_block, promise, seed=SEED):
    """Pool individual orders across the requested selections."""
    positive_number(promise, "Promise")
    if zone != "all" and zone not in ZONES:
        raise ValueError(f"Zone must be one of {ZONES} or 'all'.")
    if time_block != "all" and time_block not in TIME_BLOCKS:
        raise ValueError(f"Time block must be one of {TIME_BLOCKS} or 'all'.")
    zones = ZONES if zone == "all" else [zone]
    blocks = TIME_BLOCKS if time_block == "all" else [time_block]
    arrays = []
    for selected_zone in zones:
        for selected_block in blocks:
            times = delivery_times(selected_zone, selected_block, promise, seed=seed)
            arrays.append(times)
    return np.concatenate(arrays)


def late_percentage(zone, time_block, promise, seed=SEED):
    """Percentage of individual orders strictly later than the promise."""
    times = selected_times(zone, time_block, promise, seed)
    if len(times) == 0:
        raise ValueError("No orders were simulated; a late percentage is undefined.")
    late_orders = np.count_nonzero(times > promise)
    return 100 * late_orders / len(times)


def average_delivery_time(zone, time_block, promise, seed=SEED):
    """Mean minutes per order, weighted naturally by pooling orders."""
    times = selected_times(zone, time_block, promise, seed)
    if len(times) == 0:
        raise ValueError("No orders were simulated; an average is undefined.")
    return float(times.mean())


def delivery_rankings(promise=PROMISE, seed=SEED):
    """Describe all 12 pairs using one reproducible sample per pair."""
    rows = []
    for zone in ZONES:
        for time_block in TIME_BLOCKS:
            times = selected_times(zone, time_block, promise, seed)
            if len(times) == 0:
                raise ValueError("No orders were simulated for a selected pair.")
            rows.append({
                "zone": zone,
                "time_block": time_block,
                "orders": len(times),
                "late_percentage": 100 * np.count_nonzero(times > promise) / len(times),
                "average_minutes": float(times.mean()),
            })
    return pd.DataFrame(rows)


def cost_per_late_order(costs=COSTS):
    """Refund plus the contribution margin lost on future orders."""
    checked = validate_costs(costs)
    return checked["refund"] + checked["churn_orders"] * checked["margin"]


def evaluate_promises(zone, time_block, promises, costs=COSTS, seed=SEED):
    """Simulate demand and delivery times anew for every tested promise."""
    if zone not in ZONES or time_block not in TIME_BLOCKS:
        raise ValueError("Choose one valid zone and one valid time block.")
    candidates = list(promises)
    if not candidates:
        raise ValueError("Provide at least one candidate promise.")
    candidates = sorted({positive_number(p, "Promise") for p in candidates})
    checked = validate_costs(costs)
    late_cost = cost_per_late_order(checked)
    rows = []
    for promise in candidates:
        times = delivery_times(zone, time_block, promise, seed=seed)
        orders = len(times)
        late_orders = int(np.count_nonzero(times > promise))
        gross_profit = orders * checked["margin"]
        late_cost_total = late_orders * late_cost
        rows.append({
            "promise": promise,
            "orders": orders,
            "late_orders": late_orders,
            "late_percentage": 100 * late_orders / orders if orders else np.nan,
            "gross_profit": gross_profit,
            "late_cost": late_cost_total,
            "net_profit": gross_profit - late_cost_total,
        })
    results = pd.DataFrame(rows)
    if results["orders"].sum() == 0:
        raise ValueError("No orders were simulated for any candidate. Try shorter promises.")
    return results


def best_promise(zone, time_block, promises, costs=COSTS, seed=SEED):
    """Return the winning minutes, four-week net profit, and candidate table.

    Sorting profit descending and promise ascending resolves exact ties in
    favor of the shorter promise. Comparisons use unrounded dollar values.
    """
    results = evaluate_promises(zone, time_block, promises, costs, seed)
    winner = results.sort_values(
        ["net_profit", "promise"], ascending=[False, True]
    ).iloc[0]
    return {
        "promise": float(winner["promise"]),
        "net_profit": float(winner["net_profit"]),
        "results": results,
    }


def promise_range(minimum, maximum):
    """Inclusive five-minute grid for the app and notebook."""
    positive_number(minimum, "Minimum promise")
    positive_number(maximum, "Maximum promise")
    if minimum > maximum:
        raise ValueError("Minimum promise must not exceed maximum promise.")
    if minimum % 5 != 0 or maximum % 5 != 0:
        raise ValueError("Range endpoints must be multiples of five minutes.")
    return list(range(int(minimum), int(maximum) + 1, 5))


def search_with_expansion(zone, time_block, costs=COSTS, seed=SEED):
    """Start at 20-90; extend boundary maxima in 25-minute increments.

    Guardrails are 5 and 180 minutes. A guardrail winner is explicitly flagged
    rather than described as an interior optimum.
    """
    minimum, maximum = 20, 90
    while True:
        result = best_promise(zone, time_block, promise_range(minimum, maximum), costs, seed)
        extend_low = result["promise"] == minimum and minimum > 5
        extend_high = result["promise"] == maximum and maximum < 180
        if not extend_low and not extend_high:
            result["minimum"] = minimum
            result["maximum"] = maximum
            result["boundary_winner"] = result["promise"] in (minimum, maximum)
            return result
        if extend_low:
            minimum = max(5, minimum - 25)
        if extend_high:
            maximum = min(180, maximum + 25)
