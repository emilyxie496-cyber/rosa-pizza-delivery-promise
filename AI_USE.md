# AI-use record

## Planning and setup

Key requests: review previous project history; create a plan for the assignment;
implement the guided work plan.

Codex read the assignment instructions, proposed a staged workflow, created a
local Python environment, installed the professor's simulator and NumPy, and
verified the supplied example using seed 1. Codex created setup_check.py to make
that first checkpoint easy to rerun. The original rosa_pizza.py was preserved.

Verified output: 210 simulated orders and mean delivery time 42.9 minutes for
Far West / Fri/Sat eve at a 45-minute promise. These are simulated results.

## Full implementation

User request: "implement our plan in this goal mode".

Codex implemented shared analysis functions, a self-contained notebook generated
from those definitions, Streamlit controls and results, and the required project
skill. The implementation explicitly applied
`.github/skills/notebook-to-streamlit/SKILL.md` to reuse notebook logic in the app.

Checks: 21 independent arithmetic, edge-case, and app-interaction tests passed;
the notebook ran from a fresh kernel with 19 code cells and two saved plots.
Main findings: Far West / Fri-Sat evening has 36.7% late orders at 45 minutes;
seed 1 recommends 55 minutes and $1,212.40 estimated net profit. Across ten
seeds, 55 minutes wins seven times and 60 minutes wins three times.

Codex reviewed rendered output and corrected dollar-sign Markdown rendering.
Publication and final browser validation status will be updated when verified.
No student review is claimed by these agent-run checks.
