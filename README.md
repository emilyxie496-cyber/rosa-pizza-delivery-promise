# Rosa's Pizza delivery promise

MMGMT 722 Assignment 1: descriptive delivery analysis and a search for the best
tested delivery promise using the professor's simulator. Staffing stays fixed.

[Open the deployed app](https://rosa-pizza-delivery-promise.streamlit.app/)
· [GitHub repository](https://github.com/emilyxie496-cyber/rosa-pizza-delivery-promise)

## Results

With seed 1 and the supplied costs, Far West / Fri-Sat evening has 36.7% late
orders at a 45-minute promise despite a 42.9-minute average delivery time.
The best tested promise is 55 minutes, with estimated four-week net profit
$1,212.40 versus -$127.40 at 45 minutes. Across seeds 1-10, 55 minutes wins
seven searches and 60 minutes wins three. These are simulated estimates.

## Run locally in VS Code

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe setup_check.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open `Rosa_Pizza_Assignment1.ipynb` and select the `.venv` interpreter as the
Python kernel. The notebook is self-contained and also runs in Colab after
installing its dependencies. It includes all required example outputs,
rankings, recommendations, charts, sensitivity analysis, and the AI appendix.

The app imports `rosa_analysis.py`. The notebook's visible function cells are
generated from that module, avoiding separate implementations. To regenerate:

```powershell
.\.venv\Scripts\python.exe build_notebook.py
.\.venv\Scripts\python.exe -m ipykernel install --prefix .venv --name rosa-pizza --display-name "Python (Rosa Pizza)"
.\.venv\Scripts\python.exe -m jupyter nbconvert --execute --to notebook --inplace Rosa_Pizza_Assignment1.ipynb
```

Regeneration replaces notebook outputs; execute it afterward. Update
`submission_links.json` before regeneration to include published URLs.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

21 checks cover all four selection cases, order-weighted calculations, exact
lateness, cost/profit arithmetic, seed repeatability, candidate regeneration,
ties, range expansion, invalid inputs, and app scenarios.
The notebook has executed successfully from a fresh kernel with 19 code cells
and two saved plots; it also passed an execution check in a directory without
the shared Python module. The rendered notebook tables and both plots were
reviewed. Streamlit Community Cloud deployment was verified in a public browser
session without login. Default inputs returned 55 minutes / $1,212.40;
North / Lunch with margin 12, refund 20, and churn 3 returned 50 minutes /
$1,928.00, matching the local calculations. All currency text was checked in
the rendered app after correcting Markdown dollar-sign escaping. The deployed
recommendation cards and chart were also inspected at a 390-pixel screen width.

## Deploy and submit

Use Streamlit Community Cloud, repository `rosa-pizza-delivery-promise`, branch
`main`, entry point `app.py`. No API key or other secrets are required.
The professor's package URL is included in `requirements.txt`.

Both published links are included in the notebook. Submit
`Rosa_Pizza_Assignment1.ipynb` to A2L after student review is complete. The supplied course PDFs and local
environment are ignored by Git and are not part of the public repository.

## Provenance and AI use

The simulator is installed from https://github.com/zhouy185/rosa-starter.git
(version 0.1.0; setup resolved commit 09f3f0b98fd2fee1ba08322bf8db12c4940590bd).
The starter package is unchanged. Default seed is 1; the same seed is reused
across segments/candidates, so samples share random streams. Churn is measured
in future orders lost. Late cost is refund plus churn times margin; net profit
is current order margin less late costs. Future losses are charged against the
four-week cohort and do not represent pure four-week cash flow.

This project is AI-assisted; see the notebook appendix and `AI_USE.md`.
The required project skill is `.github/skills/notebook-to-streamlit/SKILL.md`.
It was explicitly read and applied during app development.
