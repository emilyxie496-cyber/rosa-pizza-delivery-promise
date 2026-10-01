---
name: notebook-to-streamlit
description: Reuse Rosa's notebook analysis in the Streamlit delivery decision app.
---

# Notebook to Streamlit

Use this skill when implementing or editing Rosa's Streamlit app.

1. Read rosa_analysis.py and the notebook's methods, cost formula, and limitations.
2. Import the shared functions into app.py; do not rewrite calculations in the UI.
3. Keep notebook function cells synchronized using build_notebook.py. The notebook
   must also run alone after installing rosa-starter and its analysis dependencies.
4. Import the supplied ZONES, TIME_BLOCKS, COSTS, and simulator without modifying
   or reproducing the professor's starter package.
5. Use seed 1 and regenerate simulated orders for every candidate promise.
6. Provide zone/time-block dropdowns, five-minute range controls, adjustable
   refund/churn/margin assumptions, and a recommendation button.
7. Validate inputs and display recommended minutes, simulated four-week net
   profit, the full candidate table, and a clearly labeled profit chart.
8. Explain that the answer is the best tested option under simulator assumptions.
   Flag endpoint winners and no-order scenarios. Do not imply certainty or a
   guaranteed real-world profit.
9. Run independent calculation tests and Streamlit AppTest for defaults, changed
   assumptions, another zone/time block, reversed ranges, and empty demand.
10. Verify the actual browser view and deployed app before declaring deployment
    complete. Keep personal information and secrets out of the public repository.
