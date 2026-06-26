import pandas as pd
from dataclasses import dataclass
from typing import List


@dataclass
class CheckResult:
    check_name: str
    status: str      # PASS / FAIL
    details: str
    failed_count: int = 0


def check_nulls(df: pd.DataFrame, critical_cols: List[str]) -> CheckResult:
    missing = [c for c in critical_cols if c not in df.columns]
    if missing:
        return CheckResult("Null Check", "FAIL",
                           f"Missing critical columns: {missing}", len(missing))
    nulls = df[critical_cols].isnull().sum()
    null_cols = nulls[nulls > 0]
    if null_cols.empty:
        return CheckResult("Null Check", "PASS", "No nulls in critical columns")
    return CheckResult("Null Check", "FAIL",
                       f"Nulls found: {null_cols.to_dict()}",
                       int(null_cols.sum()))


def check_duplicates(df: pd.DataFrame, id_col: str) -> CheckResult:
    dupes = int(df[id_col].duplicated().sum())
    if dupes == 0:
        return CheckResult("Duplicate ID Check", "PASS",
                           f"No duplicate {id_col} values")
    return CheckResult("Duplicate ID Check", "FAIL",
                       f"{dupes} duplicate {id_col} values found", dupes)


def check_value_range(df: pd.DataFrame, col: str,
                      min_val: float, max_val: float) -> CheckResult:
    if col not in df.columns:
        return CheckResult(f"Range Check [{col}]", "FAIL", f"Column '{col}' not found", 0)
    out = int(df[(df[col] < min_val) | (df[col] > max_val)].shape[0])
    if out == 0:
        return CheckResult(f"Range Check [{col}]", "PASS",
                           f"All values in [{min_val}, {max_val}]")
    return CheckResult(f"Range Check [{col}]", "FAIL",
                       f"{out} values outside [{min_val}, {max_val}]", out)


def check_allowed_values(df: pd.DataFrame, col: str,
                         allowed: List[str]) -> CheckResult:
    if col not in df.columns:
        return CheckResult(f"Allowed Values [{col}]", "FAIL",
                           f"Column '{col}' not found", 0)
    invalid = int(df[~df[col].isin(allowed)].shape[0])
    if invalid == 0:
        return CheckResult(f"Allowed Values [{col}]", "PASS",
                           "All values in allowed set")
    bad_vals = df[~df[col].isin(allowed)][col].unique().tolist()
    return CheckResult(f"Allowed Values [{col}]", "FAIL",
                       f"{invalid} invalid values found: {bad_vals[:5]}", invalid)


def check_positive_loan_amount(df: pd.DataFrame) -> CheckResult:
    neg = int(df[df['loan_amount'] <= 0].shape[0])
    if neg == 0:
        return CheckResult("Positive Loan Amount", "PASS",
                           "All loan amounts are positive")
    return CheckResult("Positive Loan Amount", "FAIL",
                       f"{neg} records with non-positive loan amounts", neg)


def check_installment_positive(df: pd.DataFrame) -> CheckResult:
    if 'installment' not in df.columns:
        return CheckResult("Positive Installment", "FAIL", "Column 'installment' not found")
    neg = int(df[df['installment'] <= 0].shape[0])
    if neg == 0:
        return CheckResult("Positive Installment", "PASS",
                           "All installment values are positive")
    return CheckResult("Positive Installment", "FAIL",
                       f"{neg} non-positive installment values", neg)


def run_all_checks(df: pd.DataFrame, config: dict) -> List[CheckResult]:
    rules = config['validation_rules']
    return [
        check_nulls(df, config['critical_columns']),
        check_duplicates(df, config['dataset']['id_column']),
        check_value_range(df, 'int_rate',
                          rules['int_rate']['min'], rules['int_rate']['max']),
        check_value_range(df, 'dti',
                          rules['dti']['min'], rules['dti']['max']),
        check_allowed_values(df, 'loan_status', rules['allowed_loan_status']),
        check_allowed_values(df, 'term', rules['allowed_term']),
        check_allowed_values(df, 'grade', rules['allowed_grade']),
        check_positive_loan_amount(df),
        check_installment_positive(df),
    ]
