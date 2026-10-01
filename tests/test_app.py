from pathlib import Path
from streamlit.testing.v1 import AppTest
from starter import COSTS
from rosa_analysis import best_promise, promise_range

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def test_default_recommendation_and_table():
    app = AppTest.from_file(APP, default_timeout=15).run()
    assert not app.exception
    assert not app.metric
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].value == "55 min"
    assert app.metric[1].value == "$1,212.40"
    assert len(app.dataframe[0].value) == 15
    assert len(app.get("vega_lite_chart")) == 1


def test_changed_costs_and_other_pair_match_shared_analysis():
    app = AppTest.from_file(APP, default_timeout=15).run()
    app.selectbox(key="zone").set_value("North")
    app.selectbox(key="block").set_value("Lunch")
    app.number_input(key="refund").set_value(20.0)
    app.number_input(key="churn").set_value(3.0)
    app.number_input(key="margin").set_value(12.0)
    app.button[0].click().run()
    expected = best_promise("North", "Lunch", promise_range(20, 90), {"refund": 20, "churn_orders": 3, "margin": 12})
    assert not app.exception
    assert app.metric[0].value == f"{expected['promise']:.0f} min"
    assert app.metric[1].value == f"${expected['net_profit']:,.2f}"


def test_invalid_range_clears_previous_results():
    app = AppTest.from_file(APP, default_timeout=15).run()
    app.button[0].click().run()
    app.number_input(key="minimum").set_value(95)
    app.button[0].click().run()
    assert not app.exception
    assert "must not exceed" in app.error[0].value
    assert not app.metric


def test_no_demand_and_endpoint_message():
    app = AppTest.from_file(APP, default_timeout=15).run()
    app.number_input(key="minimum").set_value(175)
    app.number_input(key="maximum").set_value(180)
    app.button[0].click().run()
    assert not app.exception
    assert "No orders" in app.error[0].value
    app.number_input(key="minimum").set_value(45)
    app.number_input(key="maximum").set_value(45)
    app.button[0].click().run()
    assert not app.exception
    assert "endpoint" in app.warning[0].value
