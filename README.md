# BankLoan-Analytics-QA

Automated data quality and KPI validation framework for banking analytics,
with AI-assisted test case generation.

![CI](https://github.com/vinay23is/BankLoan-Analytics-QA/actions/workflows/validate.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![pytest](https://img.shields.io/badge/tested%20with-pytest-green)

---

## Business Problem

Banking analytics teams publish dashboards showing key metrics like NPA ratio,
average interest rate, and total loan disbursements to senior management.
When source data has quality issues — duplicates, nulls, out-of-range values —
or when KPI calculations diverge from agreed business definitions, wrong numbers
reach decision-makers.

This project automates the validation layer that runs **before** report publication:
checking data quality, reconciling KPIs across computation methods, enforcing
banking business rules, and generating test scenarios from plain-text requirements
using AI.

---

## What This Project Does

| Layer | Tool | What it validates |
|---|---|---|
| **Data Quality** | pandas + pytest | Nulls, duplicates, range checks, allowed values |
| **Business Rules** | pytest | Funded ≤ loan amount, valid status/grade/term, positive amounts |
| **KPI Reconciliation** | pandas + SQLite | pandas-computed KPIs vs SQL-computed KPIs |
| **AI Test Generation** | Claude API | Plain-text requirements → pytest test outlines |
| **Test Report** | Python + Markdown | Data quality score, KPI table, pass/fail summary |
| **CI/CD** | GitHub Actions | Automatic suite execution on every push |

---

## Dataset

Uses the publicly available synthetic bank loan dataset (~38,000 rows) widely
used in banking analytics projects.

**Download:** See [`data/README_dataset.md`](data/README_dataset.md) for sources.

**Key fields:** `id`, `loan_amount`, `funded_amount`, `int_rate`, `loan_status`
(Fully Paid / Current / Charged Off), `grade`, `term`, `dti`, `annual_income`

---

## Architecture

```
financial_loan.csv
        │
        ▼
┌─────────────────────┐     ┌──────────────────────┐
│  Data Quality Layer  │     │  Business Rules Layer │
│  (data_quality.py)   │     │  (test_business_rules)│
│  9 automated checks  │     │  9 rule assertions    │
└──────────┬──────────┘     └───────────┬───────────┘
           │                             │
           ▼                             ▼
┌─────────────────────────────────────────────────┐
│              KPI Calculator                      │
│  compute_kpis_pandas()  compute_kpis_sql()       │
│  (pandas reference)     (SQLite SQL reference)   │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
           ┌────────────────────┐
           │  KPI Reconciler    │
           │  reconcile()       │
           │  tolerance=0.01    │
           └────────┬───────────┘
                    │
                    ▼
     ┌──────────────────────────┐
     │  AI Test Generator       │
     │  requirements → Claude   │
     │  → pytest outlines       │
     └──────────┬───────────────┘
                │
                ▼
     ┌──────────────────────┐
     │  Markdown QA Report  │
     │  sample_report.md    │
     └──────────────────────┘
                │
                ▼
     ┌──────────────────────┐
     │  GitHub Actions CI   │
     │  runs on every push  │
     └──────────────────────┘
```

---

## Banking KPIs Validated

| KPI | Formula |
|---|---|
| Good Loan Rate (%) | (Fully Paid + Current) / Total × 100 |
| Bad Loan Rate / NPA Proxy (%) | Charged Off / Total × 100 |
| Average Interest Rate | mean(int_rate) |
| Average Funded Amount | mean(funded_amount) |
| Total Capital Deployed | sum(funded_amount) |
| Total Loan Applications | COUNT(*) |

---

## KPI Reconciliation Approach

KPIs are computed via two independent methods — **pandas** and **SQLite SQL** —
and compared using a configurable tolerance threshold. Any mismatch flags a
potential calculation error in the reporting layer.

> In a production environment, one side would be replaced by a live Power BI
> REST API export or a direct query against the reporting warehouse.

---

## AI-Assisted Test Generation

`ai_testing/test_generator.py` sends plain-text banking business requirements
to the Claude API and receives pytest function outlines in return.

**Example input** (`ai_testing/requirements_input.txt`):
```
REQ-01: The Bad Loan Rate (NPA proxy) must equal the count of Charged Off loans
divided by total loan applications, expressed as a percentage rounded to 2 decimal places.
```

**Generated output** (reviewed before committing):
```python
def test_bad_loan_rate_equals_charged_off_percentage():
    ...
```

See [`ai_testing/generated/sample_ai_tests.py`](ai_testing/generated/sample_ai_tests.py)
for committed example output.

---

## Sample Test Report

See [`reports/sample_report.md`](reports/sample_report.md) for a full example
(generated after downloading the dataset).

```
Data Quality Score:    94/100  (8/9 checks passed)
KPI Reconciliation:    6/6 KPIs matched within tolerance
Business Rules:        9/9 passed
```

---

## How to Run Locally

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/BankLoan-Analytics-QA
cd BankLoan-Analytics-QA

# Install
pip install -r requirements.txt

# Download dataset → place as data/financial_loan.csv
# (see data/README_dataset.md for sources)

# Run full test suite
pytest tests/ -v

# Generate Markdown report
python reports/generate_report.py

# AI test generation (requires Claude API key)
export ANTHROPIC_API_KEY=sk-ant-...
python ai_testing/test_generator.py
```

---

## Project Limitations

- **KPI reconciliation** uses two local computation methods (pandas vs SQLite SQL)
  as a proxy for source-vs-BI-layer reconciliation. In production, one side
  would be a Power BI REST API export or live reporting query.
- **Dataset** is synthetic and publicly available — not real banking data.
- **AI test generation** requires an Anthropic API key.
  `sample_ai_tests.py` is committed for reference without needing a key.
- **No anomaly detection** on monthly KPI time series — noted as future scope.
- **No Power BI or Tableau integration** — focus is on data-layer QA.

---

## Future Improvements

- Connect to Power BI REST API for live KPI reconciliation
- Add dbt test layer as an alternative validation method
- Statistical anomaly detection on monthly KPI trends (Z-score, IQR)
- Extend business rules to cover regulatory KPIs (LCR, NSFR)
- HTML report with visual summary charts

---

## Interview Talking Points

1. **Problem framing:** "Analytics QA engineers validate that BI reports accurately reflect source data. I automated that validation."
2. **KPI reconciliation:** "I compute the same KPI two ways and compare them. In production you replace one side with a Power BI export."
3. **Business rules:** "Each banking rule is an executable pytest test — not just documentation. This catches silent regressions."
4. **AI testing:** "I used Claude to generate test outlines from requirements. The AI accelerates authoring; a human reviews before running."
5. **Limitations:** "Dataset is synthetic, BI layer is simulated, anomaly detection is future scope. All documented clearly."

---

## Tech Stack

`Python 3.11` · `pandas` · `pytest` · `SQLite` · `PyYAML` · `Jinja2` · `Claude API` · `GitHub Actions`
