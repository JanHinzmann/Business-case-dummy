# Business Case Calculator

A compact Streamlit app for evaluating a proposed investment or initiative. It turns a few editable assumptions into a decision-ready summary, financial metrics, annual cash flows, and a downloadable CSV.

## Features

- Editable assumptions for investment, benefits, operating costs, time horizon, discount rate, and optional benefit growth
- EUR, USD, and GBP display options
- NPV, ROI, benefit-cost ratio, net annual benefit, payback period, and break-even year
- Partial-year payback estimates when payback occurs within the selected horizon
- Annual, discounted, and cumulative cash-flow details
- Interactive cash-flow chart and CSV export
- Input guardrails and warnings for unusual assumptions
- No account, database, API, secrets, or external service required

## Run locally

Use Python 3.10 or newer. From the repository root:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the runtime dependencies and start the app:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints the local URL, normally `http://localhost:8501`.

## Run the tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

You can also check that the Python source compiles:

```bash
python -m compileall app.py business_case.py tests
```

## Calculation definitions

The model treats the initial investment as a cash outflow at year 0. Annual benefits and operating costs occur at the end of each subsequent year. Benefit growth compounds annually when enabled; operating cost remains flat.

- **Net annual benefit:** first-year benefit minus annual operating cost.
- **Total benefits:** sum of undiscounted annual benefits over the selected period.
- **Total costs:** initial investment plus undiscounted operating costs over the selected period.
- **ROI:** `(total benefits - total costs) / total costs`. The result is unavailable when total cost is zero.
- **NPV:** initial investment plus all annual net cash flows, discounted to year 0 at the selected discount rate.
- **Benefit-cost ratio:** discounted benefits divided by discounted investment and operating costs. The result is unavailable when discounted cost is zero.
- **Payback period:** the point when cumulative undiscounted cash flow becomes non-negative. If a positive annual cash flow crosses zero, the remaining fraction of that year is estimated linearly.
- **Break-even year:** the first whole year in which cumulative undiscounted cash flow is non-negative.

Payback and break-even show **Not reached** when the investment is not recovered inside the selected analysis period.

## Deploy to Streamlit Community Cloud

1. Put `app.py`, `business_case.py`, `requirements.txt`, and `.streamlit/config.toml` in the GitHub repository and push the branch you want to deploy. Keep `requirements.txt` in the repository root alongside `app.py`.
2. Sign in at [share.streamlit.io](https://share.streamlit.io/) with GitHub. The connected GitHub account needs admin permission for the repository; grant additional access if the repository is private.
3. In the Streamlit workspace, select **Create app**.
4. When asked whether you already have an app, choose **Yup, I have an app**.
5. Select the GitHub repository and branch, then set the entrypoint file to `app.py`. You can instead use **Paste GitHub URL** and provide the URL to `app.py`.
6. Optionally choose an `*.streamlit.app` subdomain, then deploy.

No secrets or Linux system packages are required. Future pushes to the deployed branch trigger app updates; changes to `requirements.txt` trigger dependency reinstallation.

For current platform details, see Streamlit's official guides for [deploying an app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) and [declaring app dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).

## Project structure

```text
.
├── .streamlit/
│   └── config.toml
├── tests/
│   └── test_business_case.py
├── app.py
├── business_case.py
├── README.md
├── requirements-dev.txt
└── requirements.txt
```

## Disclaimer

The results are estimates based solely on the entered assumptions. Validate material decisions against your organization's finance and risk standards.
