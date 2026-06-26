"""
Generates a Markdown test execution report for the banking analytics QA suite.
Run after downloading the dataset:  python reports/generate_report.py
"""
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import yaml

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation.data_quality import run_all_checks
from validation.kpi_calculator import compute_kpis_pandas, compute_kpis_sql, KPI_DEFINITIONS
from validation.kpi_reconciler import reconcile


def load_config() -> dict:
    return yaml.safe_load(Path("config.yaml").read_text())


def build_report(df: pd.DataFrame, config: dict) -> str:
    dq_results    = run_all_checks(df, config)
    pandas_kpis   = compute_kpis_pandas(df)
    sql_kpis      = compute_kpis_sql(df)
    recon_results = reconcile(pandas_kpis, sql_kpis,
                              config['reconciliation']['tolerance'])

    passed_dq    = sum(1 for r in dq_results    if r.status == "PASS")
    passed_recon = sum(1 for r in recon_results if r.status == "PASS")
    total_dq     = len(dq_results)
    total_recon  = len(recon_results)
    dq_score     = round(passed_dq / total_dq * 100)

    lines = [
        "# BankLoan-Analytics-QA: Test Execution Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"**Dataset:** `{config['dataset']['path']}`  ",
        f"**Total Records:** {len(df):,}",
        "",
        "---",
        "",
        f"## Data Quality Score: {dq_score}/100  ({passed_dq}/{total_dq} checks passed)",
        "",
        "| Check | Status | Details | Failed Rows |",
        "|---|---|---|---|",
    ]
    for r in dq_results:
        icon = "✅" if r.status == "PASS" else "❌"
        lines.append(
            f"| {r.check_name} | {icon} {r.status} | {r.details} | {r.failed_count} |"
        )

    lines += [
        "",
        "---",
        "",
        f"## KPI Reconciliation: {passed_recon}/{total_recon} KPIs matched",
        "",
        "> Pandas (reference) vs SQLite SQL — both methods should agree within tolerance.",
        "> In production, the SQL side would be replaced by a Power BI export or REST API.",
        "",
        "| KPI | Definition | Pandas | SQL | Δ Difference | Status |",
        "|---|---|---|---|---|---|",
    ]
    for r in recon_results:
        icon = "✅" if r.status == "PASS" else "❌"
        defn = KPI_DEFINITIONS.get(r.kpi_name, "")
        lines.append(
            f"| {r.kpi_name} | {defn} | {r.pandas_value} "
            f"| {r.sql_value} | {r.difference} | {icon} {r.status} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Banking KPI Summary",
        "",
    ]
    for k, v in pandas_kpis.items():
        defn = KPI_DEFINITIONS.get(k, "")
        lines.append(f"- **{k}**: `{v}` — {defn}")

    lines += [
        "",
        "---",
        "",
        "## Suite Summary",
        "",
        f"| Category | Passed | Total | Score |",
        f"|---|---|---|---|",
        f"| Data Quality | {passed_dq} | {total_dq} | {dq_score}% |",
        f"| KPI Reconciliation | {passed_recon} | {total_recon} | "
        f"{round(passed_recon/total_recon*100)}% |",
    ]
    return "\n".join(lines)


def main():
    config    = load_config()
    data_path = Path(config['dataset']['path'])

    if not data_path.exists():
        print(
            f"Dataset not found at {data_path}.\n"
            "Download financial_loan.csv from Kaggle or a public GitHub mirror\n"
            "and place it in the data/ folder."
        )
        sys.exit(1)

    print(f"Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"  {len(df):,} rows loaded.")

    report    = build_report(df, config)
    out_path  = Path("reports/sample_report.md")
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(report)

    print(f"\nReport written to {out_path}")


if __name__ == "__main__":
    main()
