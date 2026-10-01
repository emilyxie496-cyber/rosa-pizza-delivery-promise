"""Rosa's decision app, using the notebook-to-streamlit project skill."""

import altair as alt
import streamlit as st
from starter import ZONES, TIME_BLOCKS, COSTS, PROMISE
from rosa_analysis import best_promise, cost_per_late_order, promise_range, SEED

st.set_page_config(page_title="Rosa's delivery promise", page_icon=":material/local_pizza:", layout="wide")
st.title("Rosa's delivery promise")
st.markdown("Choose a delivery promise that balances order demand and the cost of late deliveries.")
st.caption("Four-week simulation · Fixed driver staffing · Current promise: 45 minutes")

with st.form("decision_inputs", border=True):
    st.subheader("Set your scenario")
    left, right = st.columns(2)
    with left:
        zone = st.selectbox("Delivery zone", ZONES, index=2, key="zone")
        minimum = st.number_input("Minimum promise (minutes)", min_value=5, max_value=180, value=20, step=5, key="minimum")
        margin = st.number_input("Profit margin per order ($)", min_value=0.0, value=float(COSTS["margin"]), step=0.5, key="margin")
    with right:
        block = st.selectbox("Time block", TIME_BLOCKS, index=2, key="block")
        maximum = st.number_input("Maximum promise (minutes)", min_value=5, max_value=180, value=90, step=5, key="maximum")
        refund = st.number_input("Refund per late order ($)", min_value=0.0, value=float(COSTS["refund"]), step=0.5, key="refund")
    churn = st.number_input("Future orders lost per late delivery", min_value=0.0, value=float(COSTS["churn_orders"]), step=0.1, key="churn")
    submitted = st.form_submit_button("Recommend a promise", type="primary", icon=":material/auto_graph:")

if submitted:
    st.session_state.pop("recommendation", None)
    try:
        costs = {"refund": refund, "churn_orders": churn, "margin": margin}
        result = best_promise(zone, block, promise_range(minimum, maximum), costs, seed=SEED)
        st.session_state["recommendation"] = (zone, block, minimum, maximum, costs, result)
    except ValueError as exc:
        st.error(str(exc))

if "recommendation" not in st.session_state:
    if not submitted:
        st.info("Set your assumptions, then click Recommend a promise.")
else:
    selected_zone, selected_block, low, high, selected_costs, result = st.session_state["recommendation"]
    table = result["results"]
    winner = table.loc[table["promise"] == result["promise"]].iloc[0]
    st.subheader(f"Recommendation for {selected_zone} · {selected_block}")
    st.caption(f"Last evaluated scenario: {low}–{high} minutes in 5-minute steps; margin {chr(92)}${selected_costs['margin']:.2f}, refund {chr(92)}${selected_costs['refund']:.2f}, future orders lost {selected_costs['churn_orders']:.1f}.")
    with st.container(horizontal=True):
        st.metric("Recommended promise", f"{result['promise']:.0f} min", border=True)
        st.metric("Estimated net profit / 4 weeks", f"${result['net_profit']:,.2f}", border=True)
        st.metric("Simulated orders", f"{int(winner['orders']):,}", border=True)
        late_display = f"{winner['late_percentage']:.1f}%" if winner["orders"] else "Undefined"
        st.metric("Late orders", late_display, border=True)
    if result["promise"] in (low, high):
        st.warning("The winner is at a range endpoint. Widen the range before settling on this promise.")
    if winner["orders"] == 0:
        st.warning("The winning option simulates no orders and zero profit. Review the costs and range before adopting it.")
    if result["net_profit"] < 0:
        st.warning("Even the best tested option loses money under these assumptions.")

    baseline = best_promise(selected_zone, selected_block, [PROMISE], selected_costs)["net_profit"]
    st.markdown(f"Compared with today's 45-minute promise, estimated net profit changes by **{chr(92)}${result['net_profit'] - baseline:+,.2f}**. Each late order costs **{chr(92)}${cost_per_late_order(selected_costs):.2f}** under this scenario.")
    st.subheader("Profit across the tested promises")
    base = alt.Chart(table).encode(
        x=alt.X("promise:Q", title="Promised delivery time (minutes)", scale=alt.Scale(zero=False)),
        y=alt.Y("net_profit:Q", title="Estimated four-week net profit ($)"),
        tooltip=[alt.Tooltip("promise:Q", title="Promise (min)"), alt.Tooltip("net_profit:Q", title="Net profit ($)", format=",.2f"), alt.Tooltip("orders:Q", title="Orders"), alt.Tooltip("late_orders:Q", title="Late orders")],
    )
    line = base.mark_line(point=True, color="#28628C")
    highlight = base.transform_filter(alt.datum.promise == result["promise"]).mark_point(size=170, color="#B06E12", filled=True)
    current = alt.Chart(table.iloc[:1]).mark_rule(strokeDash=[5, 4], color="#666666").encode(x=alt.datum(45))
    chart = (line + highlight + current).properties(height=310)
    st.altair_chart(chart)
    st.caption("Gold point: recommended option. Dashed line: current 45-minute promise. All estimates use seed 1.")
    st.subheader("Candidate results")
    st.dataframe(table, hide_index=True, column_config={
        "promise": st.column_config.NumberColumn("Promise (min)", format="%.0f"),
        "orders": "Orders", "late_orders": "Late orders",
        "late_percentage": st.column_config.NumberColumn("Late (%)", format="%.1f"),
        "gross_profit": st.column_config.NumberColumn("Order margin ($)", format="$%.2f"),
        "late_cost": st.column_config.NumberColumn("Late cost ($)", format="$%.2f"),
        "net_profit": st.column_config.NumberColumn("Net profit ($)", format="$%.2f"),
    })

with st.expander("How the recommendation works"):
    st.markdown("A longer promise reduces demand; fewer orders also reduce delivery congestion. We simulate each candidate separately and subtract refund plus lost future margin for every delivery beyond the promise. Exact ties favor the shorter promise.")
    st.code("late cost = refund + future orders lost × margin\nnet profit = orders × margin − late orders × late cost", language=None)
    st.markdown("The recommendation is the best among the tested options under the simulator and chosen costs. It is not a guarantee of real-world profit. Staffing stays fixed; simulation randomness and uncertain churn assumptions can change the winner.")
