"""
Sample AI-generated test cases for banking loan analytics data validation.
Produced from requirements in ai_testing/requirements_input.txt using Claude,
then reviewed before committing.

This file demonstrates how LLMs can convert plain-text business requirements
into executable pytest functions, accelerating test authoring in analytics QA.
"""
import pandas as pd
import pytest


# Requirement: REQ-01 — Bad Loan Rate (NPA proxy) calculation
def test_bad_loan_rate_equals_charged_off_percentage():
    df = pd.DataFrame({
        'loan_status': ['Fully Paid', 'Current', 'Charged Off',
                        'Fully Paid', 'Charged Off']
    })
    total        = len(df)
    charged_off  = (df['loan_status'] == 'Charged Off').sum()
    expected_pct = round(charged_off / total * 100, 2)
    assert expected_pct == 40.0, (
        f"Expected bad loan rate 40.0%, got {expected_pct}%"
    )


# Requirement: REQ-02 — All loan amounts must be positive values greater than zero
def test_loan_amount_is_positive():
    df = pd.DataFrame({
        'loan_amount': [10000, 15000, 20000],
    })
    non_positive = df[df['loan_amount'] <= 0]
    assert len(non_positive) == 0, (
        f"{len(non_positive)} records with non-positive loan_amount"
    )


# Requirement: REQ-03 — Interest rates must be between 5% and 30%
def test_interest_rate_within_valid_lending_range():
    df = pd.DataFrame({'int_rate': [7.5, 12.0, 18.5, 24.9, 29.99]})
    below_min = (df['int_rate'] < 5.0).sum()
    above_max = (df['int_rate'] > 30.0).sum()
    assert below_min == 0, f"{below_min} interest rate(s) below 5%"
    assert above_max == 0, f"{above_max} interest rate(s) above 30%"


# Requirement: REQ-04 — Grade must be A through G only
def test_loan_grade_restricted_to_valid_set():
    df          = pd.DataFrame({'grade': ['A', 'B', 'C', 'D', 'E', 'F', 'G']})
    valid_grades = set('ABCDEFG')
    invalid      = df[~df['grade'].isin(valid_grades)]
    assert len(invalid) == 0, (
        f"Invalid grade values found: {invalid['grade'].unique().tolist()}"
    )


# Requirement: REQ-05 — DTI must be non-negative and not exceed 100
def test_dti_within_valid_range():
    df         = pd.DataFrame({'dti': [0.0, 15.5, 42.3, 99.9, 100.0]})
    below_zero = (df['dti'] < 0).sum()
    above_max  = (df['dti'] > 100).sum()
    assert below_zero == 0, f"{below_zero} DTI value(s) are negative"
    assert above_max  == 0, f"{above_max} DTI value(s) exceed 100"
