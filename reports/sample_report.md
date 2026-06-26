# BankLoan-Analytics-QA: Test Execution Report

**Generated:** 2026-06-26 16:03  
**Dataset:** `data/financial_loan.csv`  
**Total Records:** 38,576

---

## Data Quality Score: 100/100  (9/9 checks passed)

| Check | Status | Details | Failed Rows |
|---|---|---|---|
| Null Check | ✅ PASS | No nulls in critical columns | 0 |
| Duplicate ID Check | ✅ PASS | No duplicate id values | 0 |
| Range Check [int_rate] | ✅ PASS | All values in [0.05, 0.3] | 0 |
| Range Check [dti] | ✅ PASS | All values in [0.0, 100.0] | 0 |
| Allowed Values [loan_status] | ✅ PASS | All values in allowed set | 0 |
| Allowed Values [term] | ✅ PASS | All values in allowed set | 0 |
| Allowed Values [grade] | ✅ PASS | All values in allowed set | 0 |
| Positive Loan Amount | ✅ PASS | All loan amounts are positive | 0 |
| Positive Installment | ✅ PASS | All installment values are positive | 0 |

---

## KPI Reconciliation: 6/6 KPIs matched

> Pandas (reference) vs SQLite SQL — both methods should agree within tolerance.
> In production, the SQL side would be replaced by a Power BI export or REST API.

| KPI | Definition | Pandas | SQL | Δ Difference | Status |
|---|---|---|---|---|---|
| good_loan_rate_pct | % of loans that are Fully Paid or Current | 86.18 | 86.18 | 0.0 | ✅ PASS |
| bad_loan_rate_pct | % of loans that are Charged Off (NPA proxy) | 13.82 | 13.82 | 0.0 | ✅ PASS |
| avg_interest_rate_pct | Average interest rate across all loans (as %) | 12.0488 | 12.0488 | 0.0 | ✅ PASS |
| avg_loan_amount | Average loan amount per application | 11296.07 | 11296.07 | 0.0 | ✅ PASS |
| total_loan_amount | Total loan capital across all applications | 435757075.0 | 435757075.0 | 0.0 | ✅ PASS |
| total_applications | Total number of loan applications in dataset | 38576.0 | 38576.0 | 0.0 | ✅ PASS |

---

## Banking KPI Summary

- **good_loan_rate_pct**: `86.18` — % of loans that are Fully Paid or Current
- **bad_loan_rate_pct**: `13.82` — % of loans that are Charged Off (NPA proxy)
- **avg_interest_rate_pct**: `12.0488` — Average interest rate across all loans (as %)
- **avg_loan_amount**: `11296.07` — Average loan amount per application
- **total_loan_amount**: `435757075.0` — Total loan capital across all applications
- **total_applications**: `38576` — Total number of loan applications in dataset

---

## Suite Summary

| Category | Passed | Total | Score |
|---|---|---|---|
| Data Quality | 9 | 9 | 100% |
| KPI Reconciliation | 6 | 6 | 100% |