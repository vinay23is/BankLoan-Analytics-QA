import pandas as pd
import pytest
from validation.kpi_calculator import compute_kpis_pandas, compute_kpis_sql
from validation.kpi_reconciler import reconcile


@pytest.fixture
def loan_df():
    """60 good loans + 40 charged off = predictable KPIs for assertions."""
    return pd.DataFrame({
        'id':            range(1, 101),
        'loan_amount':   [10000] * 100,
        'funded_amount': [9500]  * 100,
        'int_rate':      [12.5]  * 60 + [18.0] * 40,
        'loan_status':   ['Fully Paid'] * 60 + ['Charged Off'] * 40,
        'grade':         ['A'] * 60 + ['C'] * 40,
        'dti':           [20.0] * 100,
    })


# --- KPI correctness ---

def test_good_loan_rate_is_60_percent(loan_df):
    kpis = compute_kpis_pandas(loan_df)
    assert kpis['good_loan_rate_pct'] == 60.0


def test_bad_loan_rate_is_40_percent(loan_df):
    kpis = compute_kpis_pandas(loan_df)
    assert kpis['bad_loan_rate_pct'] == 40.0


def test_good_and_bad_rates_sum_to_100(loan_df):
    kpis = compute_kpis_pandas(loan_df)
    assert abs(kpis['good_loan_rate_pct'] + kpis['bad_loan_rate_pct'] - 100.0) < 0.01


def test_total_applications_matches_row_count(loan_df):
    kpis = compute_kpis_pandas(loan_df)
    assert kpis['total_applications'] == len(loan_df)


# --- Reconciliation: pandas vs SQL must agree ---

def test_pandas_and_sql_kpis_agree(loan_df):
    pandas_kpis = compute_kpis_pandas(loan_df)
    sql_kpis    = compute_kpis_sql(loan_df)
    results     = reconcile(pandas_kpis, sql_kpis, tolerance=0.01)
    failures    = [r for r in results if r.status == "FAIL"]
    assert len(failures) == 0, (
        f"KPI mismatches detected:\n"
        + "\n".join(f"  {r.kpi_name}: pandas={r.pandas_value}, sql={r.sql_value}, diff={r.difference}"
                    for r in failures)
    )


def test_reconciler_catches_deliberate_discrepancy():
    """Confirms the reconciler flags a known-bad value — the core QA capability."""
    pandas_kpis = {'good_loan_rate_pct': 60.0}
    sql_kpis    = {'good_loan_rate_pct': 62.5}   # simulates a BI layer calculation error
    results = reconcile(pandas_kpis, sql_kpis, tolerance=0.01)
    assert results[0].status == "FAIL"
    assert results[0].difference == pytest.approx(2.5, abs=0.001)


def test_reconciler_passes_within_tolerance():
    pandas_kpis = {'avg_interest_rate': 14.8500}
    sql_kpis    = {'avg_interest_rate': 14.8502}   # floating-point rounding difference
    results = reconcile(pandas_kpis, sql_kpis, tolerance=0.01)
    assert results[0].status == "PASS"
