"""Generate the single-file submission from the shared analysis definitions."""

import inspect
import json
from pathlib import Path

import nbformat as nbf
import rosa_analysis as analysis

ROOT = Path(__file__).resolve().parent
cells = []


def markdown(text):
    cells.append(nbf.v4.new_markdown_cell(text.strip().replace('$', chr(92) + '$')))


def code(text):
    cells.append(nbf.v4.new_code_cell(text.strip()))


def functions(*names):
    code("\n\n".join(inspect.getsource(getattr(analysis, name)).strip() for name in names))


links_path = ROOT / "submission_links.json"
links = json.loads(links_path.read_text(encoding="utf-8")) if links_path.exists() else {}
detail = analysis.search_with_expansion("Far West", "Fri/Sat eve")
baseline = analysis.best_promise("Far West", "Fri/Sat eve", [45])["net_profit"]

markdown(f"""
# Rosa's Pizza: finding the best delivery promise
**MMGMT 722 · Assignment 1**

## Summary
For Far West on Friday/Saturday evening, **{analysis.late_percentage('Far West', 'Fri/Sat eve', 45):.1f}%**
of simulated orders miss today's 45-minute promise, although the average delivery
time is **{analysis.average_delivery_time('Far West', 'Fri/Sat eve', 45):.1f} minutes**.
Using the supplied costs and seed 1, **{detail['promise']:.0f} minutes** is the best
tested promise in the 20–90 minute grid. Estimated four-week net profit is
**${detail['net_profit']:,.2f}**, compared with **${baseline:,.2f}** at 45 minutes.

The analysis below follows Parts I(a–e) and II(a–b). Part III links and the AI-use
appendix are at the end. Results are simulated, not records of real deliveries.
""")
markdown("""
## Context, method, and assumptions
Rosa must balance demand against refunds and the future profit lost after late
deliveries. A shorter promise attracts more orders but also increases congestion.
Staffing is fixed; changing staffing, delivery zones, and pricing is outside this assignment.

- Source: the supplied *Assignment 1 – Finding the Best Delivery Promise for Rosa's Pizza*.
- Background: supplied *1. Introduction to DA*, especially the contrast between means and late-delivery tails.
- Data: the professor's `rosa-starter` package, imported without changes.
- One array entry represents one order's delivery time in minutes; each array covers four weeks in one pair.
- Lateness is strictly `delivery time > promise`; exactly on the promise is on time.
- Default seed is 1 for reproducibility. The same seed is reused for each pair and
  candidate; samples therefore share random streams. This is a controlled comparison,
  not an independence assumption or a confidence interval.
- Pooled measures weight each **order**, not each zone/time block, equally.
- Profit is a four-week accounting estimate with future churn loss charged to
  the late orders in that period. It is not a pure four-week cash-flow forecast.
""")
markdown("""
## Setup
In VS Code, select the project's `.venv` Python kernel. This notebook also runs
as a single file in Colab or local Jupyter: it includes the same function definitions
as the app's shared module and does not require that module to be beside it.

The next cell installs dependencies only if they are missing. In a fresh notebook
environment, the professor's installation command is
`%pip install git+https://github.com/zhouy185/rosa-starter.git`.
""")
code("""
import importlib.util
import subprocess
import sys

packages = {'numpy': 'numpy', 'pandas': 'pandas', 'matplotlib': 'matplotlib',
            'starter': 'git+https://github.com/zhouy185/rosa-starter.git'}
missing = [package for module, package in packages.items()
           if importlib.util.find_spec(module) is None]
if missing:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
""")
code("""
import math
from numbers import Real
from importlib.metadata import version
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
from starter import ZONES, TIME_BLOCKS, COSTS, PROMISE, delivery_times

SEED = 1
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False,
                     'axes.spines.right': False, 'figure.dpi': 120})
pd.options.display.float_format = '{:,.2f}'.format
print('Zones:', ZONES)
print('Time blocks:', TIME_BLOCKS)
print('Costs:', COSTS)
print('Package versions:', {name: version(name) for name in ['rosa-starter', 'numpy', 'pandas']})
""")
markdown("""
### First example: what the array means
`delivery_times` is a function: we supply a zone, time block, promise, and seed.
`len(times)` counts orders. `times.mean()` averages the individual times, and
`round(..., 1)` changes only the displayed precision. We retain full precision
for calculation and comparison.
""")
code("""
times = delivery_times('Far West', 'Fri/Sat eve', PROMISE, seed=SEED)
print(len(times), 'orders; average delivery time', round(times.mean(), 1), 'minutes')
print('First five order delivery times:', times[:5])
""")
markdown("""
## Part I(a): percentage of late orders
First choose the applicable zones and blocks. A `for` loop visits each pair;
`np.concatenate` pools individual orders into one array. This prevents an
unweighted average of group percentages from giving small groups too much weight.

`times > promise` compares every order with the promise and creates True/False
values. `np.count_nonzero` counts True values (late orders).

**Late percentage = 100 × total late orders / total orders.**
""")
functions("positive_number", "validate_costs", "selected_times", "late_percentage")
code("""
examples = [('Far West', 'Fri/Sat eve'), ('all', 'Lunch'),
            ('North', 'all'), ('all', 'all')]
late_examples = pd.DataFrame([
    {'Zone': zone, 'Time block': block, 'Late (%)': late_percentage(zone, block, PROMISE)}
    for zone, block in examples
])
display(late_examples.round(2))
""")
markdown("""
## Part I(b): rank all pairs by late rate
Each row below is one of the three zones × four time blocks. `sort_values`
orders the rows from the highest late percentage to the lowest. Exact ties are
ordered by zone and time-block name for consistent presentation.
""")
functions("delivery_rankings")
code("""
ranking_data = delivery_rankings(PROMISE)
late_ranking = ranking_data.sort_values(
    ['late_percentage', 'zone', 'time_block'], ascending=[False, True, True]
).reset_index(drop=True)
display(late_ranking.rename(columns={
    'zone': 'Zone', 'time_block': 'Time block', 'orders': 'Orders',
    'late_percentage': 'Late (%)', 'average_minutes': 'Average (min)'
}).round(2))
""")
markdown("""
## Part I(c): average delivery time
Pool the same selected orders, then calculate the mean. This gives each order
equal weight. If no orders are simulated, the function raises a clear error
rather than reporting an undefined rate or average as zero.
""")
functions("average_delivery_time")
code("""
average_examples = pd.DataFrame([
    {'Zone': zone, 'Time block': block,
     'Average delivery time (min)': average_delivery_time(zone, block, PROMISE)}
    for zone, block in examples
])
display(average_examples.round(2))
""")
markdown("""
## Part I(d): rank all pairs by average delivery time
Use the same simulated observations as the late ranking so differences in the
rankings reflect the measures rather than fresh simulation draws.
""")
code("""
average_ranking = ranking_data.sort_values(
    ['average_minutes', 'zone', 'time_block'], ascending=[False, True, True]
).reset_index(drop=True)
display(average_ranking.rename(columns={
    'zone': 'Zone', 'time_block': 'Time block', 'orders': 'Orders',
    'late_percentage': 'Late (%)', 'average_minutes': 'Average (min)'
}).round(2))

fig, axes = plt.subplots(1, 2, figsize=(14, 7), layout='constrained')
for ax, table, metric, label, color in [
    (axes[0], late_ranking, 'late_percentage', 'Late orders (%)', '#28628C'),
    (axes[1], average_ranking, 'average_minutes', 'Average delivery time (minutes)', '#536C57')
]:
    labels = table['zone'] + ' | ' + table['time_block']
    ax.barh(labels, table[metric], color=color)
    ax.invert_yaxis()
    ax.set_xlim(left=0)
    ax.set_xlabel(label)
    ax.set_title('Ranking by ' + ('late rate' if metric == 'late_percentage' else 'average time'))
    ax.grid(axis='x', alpha=0.2)
fig.suptitle('All 12 delivery pairs: four-week simulation at a 45-minute promise (seed 1)')
plt.show()
""")
markdown("""
## Part I(e): which measure better supports Rosa's decision?
The **late percentage** is more directly relevant because refunds and lost future
margin are triggered by crossing the promise. Mean time alone does not describe
that costly tail. For a complete financial decision, we also need order volumes
and costs, as addressed in Part II.
""")
code("""
worst = late_ranking.iloc[0]
far_lunch = ranking_data.query("zone == 'Far West' and time_block == 'Lunch'").iloc[0]
central_lunch = ranking_data.query("zone == 'Central' and time_block == 'Lunch'").iloc[0]
display(Markdown(
    f"**Evidence:** {worst.zone} / {worst.time_block} has the highest late rate "
    f"({worst.late_percentage:.1f}%) and average time ({worst.average_minutes:.1f} min). "
    "Its mean remains below 45 minutes, but more than one third of orders are late. "
    f"Far West / Lunch averages {far_lunch.average_minutes:.1f} minutes with "
    f"{far_lunch.late_percentage:.2f}% late, whereas Central / Lunch averages "
    f"{central_lunch.average_minutes:.1f} minutes with {central_lunch.late_percentage:.2f}% late. "
    "Thus, a higher average does not necessarily mean a higher late rate in a finite sample. "
    "Both rankings identify weekend evenings as important, but late rates more directly "
    "describe failure to meet the customer promise."
))
""")
markdown("""
## Part II(a): cost per late order
Refund is an immediate cost. Churn is measured in **future orders lost**, not a
percentage of customers. Multiply those lost orders by margin to express the
future loss in dollars, then add the refund.
""")
functions("cost_per_late_order")
code("""
late_cost = cost_per_late_order(COSTS)
print(f"Cost per late order = ${COSTS['refund']:.2f} + {COSTS['churn_orders']:.1f} × ${COSTS['margin']:.2f} = ${late_cost:.2f}")
""")
markdown("""
## Part II(b): search for the most profitable promise
### Choosing the range
Begin with **20–90 minutes inclusive, in five-minute steps**. This covers promises
well below and above today's 45 minutes and the observed mean times. It is a
deliberately broad starting range, not a range chosen to force the slide's answer.
For each pair, extend the relevant boundary by 25 minutes if its winner is at an
endpoint. Stop at an interior winner or the practical guardrails of 5 and 180 minutes;
flag a guardrail winner as unresolved boundary evidence.

An interior winner suggests the grid brackets the useful trade-off, but does
not prove a global optimum or identify a best promise between grid values.

### Profit calculation and reusable interface
For **every candidate**, call the simulator again: demand and delivery congestion
change with the promise. Do not reuse a fixed 45-minute order sample.

`best_promise(zone, time_block, promises, costs, seed=1)` returns a dictionary with
`promise`, `net_profit`, and `results` (a table covering every tested candidate).
Exact profit ties favor the shorter promise; selection uses unrounded values.

**Net profit = orders × margin − late orders × (refund + churn orders × margin).**
""")
functions("evaluate_promises", "best_promise", "promise_range", "search_with_expansion")
code("""
detail = search_with_expansion('Far West', 'Fri/Sat eve', COSTS)
candidate_results = detail['results']
current = best_promise('Far West', 'Fri/Sat eve', [PROMISE], COSTS)
print(f"Range checked: {detail['minimum']}–{detail['maximum']} minutes, step 5")
print(f"Recommended promise: {detail['promise']:.0f} minutes")
print(f"Estimated four-week net profit: ${detail['net_profit']:,.2f}")
print(f"Current 45-minute promise: ${current['net_profit']:,.2f}")
print(f"Estimated improvement: ${detail['net_profit'] - current['net_profit']:,.2f}")
display(candidate_results.rename(columns={
    'promise': 'Promise (min)', 'orders': 'Orders', 'late_orders': 'Late orders',
    'late_percentage': 'Late (%)', 'gross_profit': 'Order margin ($)',
    'late_cost': 'Late costs ($)', 'net_profit': 'Net profit ($)'
}).round(2))
""")
code("""
fig, ax = plt.subplots(figsize=(9, 5), layout='constrained')
ax.plot(candidate_results['promise'], candidate_results['net_profit'],
        marker='o', color='#28628C', label='Simulated net profit')
ax.scatter([detail['promise']], [detail['net_profit']], color='#B06E12', s=100,
           zorder=3, label=f"Best tested: {detail['promise']:.0f} min")
ax.axvline(PROMISE, color='#666666', linestyle='--', label='Current promise: 45 min')
ax.axhline(0, color='#777777', linewidth=0.8)
ax.set_xlabel('Promised delivery time (minutes)')
ax.set_ylabel('Estimated four-week net profit ($)')
ax.set_title('Far West / Fri–Sat evening: profit versus promise\\nSupplied costs, fixed staffing, seed 1')
ax.grid(alpha=0.2)
ax.legend(loc='lower right')
plt.show()
""")
markdown("""
### Recommendations across all pairs
The table compares each pair's best tested option with its current 45-minute
promise using the same costs and seed. These are pair-level recommendations,
not a model of system-wide staffing changes or cross-zone operational effects.
""")
code("""
recommendations = []
for zone in ZONES:
    for block in TIME_BLOCKS:
        result = search_with_expansion(zone, block, COSTS)
        baseline = best_promise(zone, block, [PROMISE], COSTS)['net_profit']
        recommendations.append({
            'Zone': zone, 'Time block': block, 'Best promise (min)': result['promise'],
            'Net profit ($)': result['net_profit'], 'At 45 min ($)': baseline,
            'Improvement ($)': result['net_profit'] - baseline,
            'Range (min)': f"{result['minimum']}–{result['maximum']}",
            'Boundary winner': result['boundary_winner'],
        })
recommendation_table = pd.DataFrame(recommendations)
display(recommendation_table.round(2))
display(Markdown(
    f"All {len(recommendation_table)} pairs have interior winners in the initial 20–90-minute grid; "
    "no range expansion was needed for seed 1. This supports using that range for the main comparison."
    if not recommendation_table['Boundary winner'].any() and (recommendation_table['Range (min)'] == '20–90').all()
    else "At least one pair required expansion or has a boundary winner; review the range columns before recommending it."
))
""")
markdown("""
### Sensitivity to simulation randomness: seeds 1–10
Repeat the Far West/weekend search across ten seeds. This is a small sensitivity
check, not a statistical confidence interval. Compare the two leading promises
within each seed as well as the per-seed winners.
""")
code("""
seed_rows = []
for seed in range(1, 11):
    result = search_with_expansion('Far West', 'Fri/Sat eve', COSTS, seed=seed)
    alternatives = evaluate_promises('Far West', 'Fri/Sat eve', [55, 60], COSTS, seed).set_index('promise')
    seed_rows.append({'Seed': seed, 'Best promise (min)': result['promise'],
                      'Best net profit ($)': result['net_profit'],
                      'Profit at 55 min ($)': alternatives.loc[55, 'net_profit'],
                      'Profit at 60 min ($)': alternatives.loc[60, 'net_profit']})
seed_results = pd.DataFrame(seed_rows)
display(seed_results.round(2))
counts = seed_results['Best promise (min)'].value_counts().sort_index()
summary = ', '.join(f'{promise:.0f} minutes wins {count}/10 seeds' for promise, count in counts.items())
display(Markdown(
    f"**Sensitivity result:** {summary}. Mean profit at 55 minutes is "
    f"{chr(92)}${seed_results['Profit at 55 min ($)'].mean():,.2f}, compared with "
    f"{chr(92)}${seed_results['Profit at 60 min ($)'].mean():,.2f} at 60 minutes. "
    "The main recommendation is 55 minutes under seed 1, but 60 minutes is a plausible alternative. "
    "Before changing real operations, validate demand, lateness, and churn assumptions with observed data."
))
""")
markdown("""
## Checks and limitations
The checks below independently count pooled late orders, sum delivery minutes,
and recompute candidate profit from the simulator. Automated project tests also
cover exact-on-time delivery, unequal group sizes, tie handling, range expansion,
invalid inputs, empty demand, and the app controls.

Limitations: the simulator is a simplified model with fixed staffing. Refund,
margin, and especially lost future orders are assumptions. A five-minute grid
does not resolve finer differences. Reusing a seed improves repeatability but
does not remove sampling uncertainty. Rankings differ from lecture examples
because these results are generated samples, not the slides' fixed data.
""")
code("""
for zone, block in examples:
    zones = ZONES if zone == 'all' else [zone]
    blocks = TIME_BLOCKS if block == 'all' else [block]
    total, late, minutes = 0, 0, 0.0
    for z in zones:
        for b in blocks:
            sample = delivery_times(z, b, PROMISE, seed=SEED)
            total += len(sample)
            late += sum(float(t) > PROMISE for t in sample)
            minutes += sum(float(t) for t in sample)
    assert np.isclose(late_percentage(zone, block, PROMISE), 100 * late / total)
    assert np.isclose(average_delivery_time(zone, block, PROMISE), minutes / total)
assert np.isclose(cost_per_late_order(COSTS), 10 + 1.8 * 9)
for row in candidate_results.itertuples():
    sample = delivery_times('Far West', 'Fri/Sat eve', row.promise, seed=SEED)
    late = sum(float(t) > row.promise for t in sample)
    assert np.isclose(row.net_profit, len(sample) * 9 - late * (10 + 1.8 * 9))
assert detail['net_profit'] == candidate_results['net_profit'].max()
assert len(late_ranking) == len(average_ranking) == len(recommendation_table) == 12
print('All notebook checks passed.')
""")
repo_link = f"[GitHub repository]({links['github']})" if links.get("github") else "GitHub repository: not published yet."
app_link = f"[Deployed Streamlit app]({links['streamlit']})" if links.get("streamlit") else "Streamlit Community Cloud app: not deployed yet."
markdown(f"""
## Part III: Streamlit app and submission links
{repo_link}

{app_link}

The app uses the same definitions in `rosa_analysis.py`, with dropdowns for one
zone/time block, a five-minute promise range, adjustable margin/refund/churn,
and a recommendation button. It displays the winning promise, estimated profit,
candidate results, and a profit chart. The project-specific skill is
`.github/skills/notebook-to-streamlit/SKILL.md`.

Local command: `python -m streamlit run app.py`.
""")
markdown("""
## AI-use appendix
**How AI was used:** Codex reviewed the assignment instructions and previous
project discussion, proposed a guided plan, configured dependencies, implemented
the functions and Streamlit UI, and organized this notebook. It generated tests,
helped interpret the executed results, and assisted with repository/deployment
work where access permitted. The required `notebook-to-streamlit` skill was
created, read, and explicitly applied when implementing the app.

**Key prompts and instructions:**
1. “Review the history before we start this” — recover prior learning preferences and project context.
2. “Create a plan for this assignment” — use the assignment PDF and lecture background.
3. “PLEASE IMPLEMENT THIS PLAN” — follow the supplied staged requirements.
4. “Implement our plan in this goal mode” — continue through the full deliverables.
5. Project implementation instruction: “Use `.github/skills/notebook-to-streamlit/SKILL.md`
   to reuse the notebook's calculation logic in the app.” This instruction was applied by Codex.

**Verification performed by the coding agent:** independent order-level
aggregation and profit checks; fixed-seed repeatability; edge-case tests; app
interaction checks; notebook execution from a fresh kernel. Browser/deployment
verification status is documented in the project README. The supplied starter
package was not edited. AI-generated explanations are based on executed outputs.

**Student review:** this notebook is AI-assisted. Before submission, I should
run the notebook, understand the functions and trade-offs, review the recommendations,
and ensure this disclosure reflects my actual use. This appendix does not claim
that student review has already occurred.
""")

notebook = nbf.v4.new_notebook(cells=cells)
notebook.metadata["kernelspec"] = {"display_name": "Python (Rosa Pizza)", "language": "python", "name": "rosa-pizza"}
notebook.metadata["language_info"] = {"name": "python"}
nbf.validate(notebook)
target = ROOT / "Rosa_Pizza_Assignment1.ipynb"
nbf.write(notebook, target)
print(f"Created {target.name}: {len(cells)} cells")
