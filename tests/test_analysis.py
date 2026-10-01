"""Independent arithmetic and boundary checks for the assignment."""

import numpy as np
import pytest
from starter import ZONES, TIME_BLOCKS, COSTS, delivery_times
import rosa_analysis as analysis


@pytest.mark.parametrize("zone,block", [
    ("Far West", "Fri/Sat eve"), ("all", "Lunch"),
    ("North", "all"), ("all", "all"),
])
def test_all_selection_cases_against_order_totals(zone, block):
    zones = ZONES if zone == "all" else [zone]
    blocks = TIME_BLOCKS if block == "all" else [block]
    count, late, total_minutes = 0, 0, 0.0
    for selected_zone in zones:
        for selected_block in blocks:
            times = delivery_times(selected_zone, selected_block, 45, seed=1)
            count += len(times)
            late += sum(float(t) > 45 for t in times)
            total_minutes += sum(float(t) for t in times)
    assert analysis.late_percentage(zone, block, 45) == pytest.approx(100 * late / count)
    assert analysis.average_delivery_time(zone, block, 45) == pytest.approx(total_minutes / count)


def test_exact_promise_is_on_time_and_pooled_rates_are_weighted(monkeypatch):
    def fake(zone, block, promise, seed=None):
        return np.array([45.0, 46.0]) if zone == "Central" else np.array([40.0] * 8)
    monkeypatch.setattr(analysis, "delivery_times", fake)
    assert analysis.late_percentage("Central", "Lunch", 45) == 50
    assert analysis.late_percentage("all", "Lunch", 45) == pytest.approx(100 / 18)


def test_cost_and_profit_are_independently_recomputed():
    assert analysis.cost_per_late_order(COSTS) == pytest.approx(26.2)
    result = analysis.best_promise("Far West", "Fri/Sat eve", [20, 45, 55, 90], COSTS)
    for row in result["results"].itertuples():
        times = delivery_times("Far West", "Fri/Sat eve", row.promise, seed=1)
        late = sum(float(t) > row.promise for t in times)
        assert row.orders == len(times)
        assert row.net_profit == pytest.approx(len(times) * 9 - late * (10 + 1.8 * 9))
    assert result["net_profit"] == result["results"]["net_profit"].max()
    repeated = analysis.best_promise("Far West", "Fri/Sat eve", [20, 45, 55, 90], COSTS)
    assert result["results"].equals(repeated["results"])


def test_tie_chooses_shortest_and_simulates_each_candidate(monkeypatch):
    calls = []
    def fake(zone, block, promise, seed=None):
        calls.append(promise)
        return np.array([10.0, 15.0])
    monkeypatch.setattr(analysis, "delivery_times", fake)
    result = analysis.best_promise("Central", "Lunch", [50, 30, 40], COSTS)
    assert result["promise"] == 30
    assert calls == [30, 40, 50]


@pytest.mark.parametrize("zone,block,promises,costs", [
    ("bad", "Lunch", [45], COSTS),
    ("Central", "bad", [45], COSTS),
    ("Central", "Lunch", [], COSTS),
    ("Central", "Lunch", [0], COSTS),
    ("Central", "Lunch", [float("nan")], COSTS),
    ("Central", "Lunch", [45], {**COSTS, "refund": -1}),
    ("Central", "Lunch", [45], {**COSTS, "margin": float("inf")}),
    ("Central", "Lunch", [45], {"margin": 9}),
])
def test_invalid_inputs(zone, block, promises, costs):
    with pytest.raises(ValueError):
        analysis.best_promise(zone, block, promises, costs)


def test_range_validation_and_no_orders(monkeypatch):
    assert analysis.promise_range(20, 90) == list(range(20, 91, 5))
    for bounds in [(90, 20), (21, 90), (0, 90)]:
        with pytest.raises(ValueError):
            analysis.promise_range(*bounds)
    monkeypatch.setattr(analysis, "delivery_times", lambda *args, **kwargs: np.array([]))
    with pytest.raises(ValueError, match="No orders"):
        analysis.best_promise("Central", "Lunch", [45], COSTS)
    with pytest.raises(ValueError, match="undefined"):
        analysis.late_percentage("Central", "Lunch", 45)
    with pytest.raises(ValueError, match="undefined"):
        analysis.average_delivery_time("Central", "Lunch", 45)


def test_expansion_moves_past_initial_boundary(monkeypatch):
    def fake(zone, block, promises, costs, seed):
        winner = min(promises, key=lambda p: abs(p - 100))
        return {"promise": winner, "net_profit": 1, "results": None}
    monkeypatch.setattr(analysis, "best_promise", fake)
    result = analysis.search_with_expansion("Central", "Lunch")
    assert result["maximum"] == 115
    assert result["promise"] == 100
    assert not result["boundary_winner"]
