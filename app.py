import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from validation.data_quality import run_all_checks
from validation.kpi_calculator import compute_kpis_pandas, compute_kpis_sql, KPI_DEFINITIONS
from validation.kpi_reconciler import reconcile

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BankLoan-Analytics-QA",
    page_icon="🏦",
    layout="wide",
)

CONFIG = {
    "dataset": {"path": "data/financial_loan.csv", "id_column": "id"},
    "critical_columns": ["loan_amount", "int_rate", "loan_status", "grade", "issue_date"],
    "validation_rules": {
        "int_rate":            {"min": 0.05, "max": 0.30},
        "dti":                 {"min": 0.0,  "max": 100.0},
        "loan_amount":         {"min": 1.0},
        "allowed_loan_status": ["Fully Paid", "Current", "Charged Off"],
        "allowed_term":        [" 36 months", " 60 months"],
        "allowed_grade":       list("ABCDEFG"),
    },
    "reconciliation": {"tolerance": 0.01},
}

# ── Load data (cached) ────────────────────────────────────────────────────────
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

@st.cache_data
def run_validation(path: str):
    df            = load_data(path)
    dq_results    = run_all_checks(df, CONFIG)
    pandas_kpis   = compute_kpis_pandas(df)
    sql_kpis      = compute_kpis_sql(df)
    recon_results = reconcile(pandas_kpis, sql_kpis,
                              CONFIG["reconciliation"]["tolerance"])
    return df, dq_results, pandas_kpis, recon_results

df, dq_results, kpis, recon_results = run_validation(CONFIG["dataset"]["path"])

passed_dq    = sum(1 for r in dq_results    if r.status == "PASS")
passed_recon = sum(1 for r in recon_results if r.status == "PASS")
dq_score     = round(passed_dq / len(dq_results) * 100)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏦 BankLoan-Analytics-QA")
st.caption(
    "Automated data quality and KPI validation framework for banking analytics · "
    f"**{len(df):,} loan records** · "
    "[GitHub](https://github.com/vinay23is/BankLoan-Analytics-QA)"
)

# ── Top summary bar ───────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Data Quality Score", f"{dq_score}/100",
          f"{passed_dq}/{len(dq_results)} checks passed")
c2.metric("KPI Reconciliation", f"{passed_recon}/{len(recon_results)} matched",
          "pandas vs SQL")
c3.metric("Good Loan Rate", f"{kpis['good_loan_rate_pct']}%",
          "Fully Paid + Current")
c4.metric("Bad Loan Rate (NPA)", f"{kpis['bad_loan_rate_pct']}%",
          "Charged Off")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 KPI Summary", "✅ Data Quality", "🔁 KPI Reconciliation", "📈 Portfolio Charts"]
)

# ── Tab 1: KPI Summary ────────────────────────────────────────────────────────
with tab1:
    st.subheader("Banking KPI Summary")
    st.caption("Computed from source data via pandas. "
               "In production, the right-hand column would be Power BI export values.")

    rows = []
    for name, value in kpis.items():
        rows.append({
            "KPI": name,
            "Definition": KPI_DEFINITIONS.get(name, ""),
            "Value": value,
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Portfolio Breakdown")

    k1, k2, k3 = st.columns(3)
    k1.metric("Avg Interest Rate", f"{kpis['avg_interest_rate_pct']:.2f}%")
    k2.metric("Avg Loan Amount",   f"${kpis['avg_loan_amount']:,.0f}")
    k3.metric("Total Capital",     f"${kpis['total_loan_amount']:,.0f}")

# ── Tab 2: Data Quality ───────────────────────────────────────────────────────
with tab2:
    st.subheader(f"Data Quality Checks — Score: {dq_score}/100")

    rows = []
    for r in dq_results:
        rows.append({
            "Check": r.check_name,
            "Status": "✅ PASS" if r.status == "PASS" else "❌ FAIL",
            "Details": r.details,
            "Failed Rows": r.failed_count,
        })
    result_df = pd.DataFrame(rows)

    def colour_status(val):
        if "PASS" in val:
            return "color: green; font-weight: bold"
        if "FAIL" in val:
            return "color: red; font-weight: bold"
        return ""

    st.dataframe(
        result_df.style.applymap(colour_status, subset=["Status"]),
        use_container_width=True,
        hide_index=True,
    )

    fail_count = sum(1 for r in dq_results if r.status == "FAIL")
    if fail_count == 0:
        st.success(f"All {len(dq_results)} data quality checks passed on {len(df):,} records.")
    else:
        st.error(f"{fail_count} check(s) failed. Review the table above.")

# ── Tab 3: KPI Reconciliation ─────────────────────────────────────────────────
with tab3:
    st.subheader("KPI Reconciliation — Pandas vs SQL")
    st.info(
        "Each KPI is computed independently via **pandas** and via **SQLite SQL**. "
        "Both methods should agree within the configured tolerance (0.01). "
        "In a production setting, the SQL column would be replaced by a Power BI REST API export.",
        icon="ℹ️",
    )

    rows = []
    for r in recon_results:
        rows.append({
            "KPI": r.kpi_name,
            "Pandas Value": r.pandas_value,
            "SQL Value":    r.sql_value,
            "Δ Difference": r.difference,
            "Tolerance":    r.tolerance,
            "Status": "✅ PASS" if r.status == "PASS" else "❌ FAIL",
        })
    recon_df = pd.DataFrame(rows)

    st.dataframe(
        recon_df.style.applymap(colour_status, subset=["Status"]),
        use_container_width=True,
        hide_index=True,
    )

    recon_fail = sum(1 for r in recon_results if r.status == "FAIL")
    if recon_fail == 0:
        st.success(f"All {len(recon_results)} KPIs reconciled — pandas and SQL agree exactly.")
    else:
        st.error(f"{recon_fail} KPI(s) failed reconciliation. Investigate the BI calculation layer.")

# ── Tab 4: Portfolio Charts ───────────────────────────────────────────────────
with tab4:
    st.subheader("Loan Portfolio Analysis")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Loan Status Distribution**")
        status_counts = df["loan_status"].value_counts().reset_index()
        status_counts.columns = ["Loan Status", "Count"]
        st.bar_chart(status_counts.set_index("Loan Status"))

    with col_b:
        st.markdown("**Loan Grade Distribution**")
        grade_counts = df["grade"].value_counts().sort_index().reset_index()
        grade_counts.columns = ["Grade", "Count"]
        st.bar_chart(grade_counts.set_index("Grade"))

    st.markdown("**Top 8 Loan Purposes**")
    purpose_counts = (
        df["purpose"]
        .value_counts()
        .head(8)
        .reset_index()
    )
    purpose_counts.columns = ["Purpose", "Count"]
    st.bar_chart(purpose_counts.set_index("Purpose"))

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "**Project:** BankLoan-Analytics-QA · "
    "**Stack:** Python · pandas · SQLite · pytest · Streamlit · GitHub Actions · "
    "[View on GitHub](https://github.com/vinay23is/BankLoan-Analytics-QA)"
)
