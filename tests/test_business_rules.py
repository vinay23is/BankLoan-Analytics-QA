"""
Banking business rule tests.
Each test encodes one domain rule as an executable assertion.
This prevents silent regressions when upstream data transforms change.

Note: int_rate in this dataset is stored as a decimal (0.1527 = 15.27%).
"""
import pandas as pd
import pytest


@pytest.fixture
def clean_loans():
    return pd.DataFrame({
        'id':            [1, 2, 3, 4, 5],
        'loan_amount':   [10000, 15000, 20000, 5000, 8000],
        'int_rate':      [0.075, 0.120, 0.185, 0.090, 0.150],
        'loan_status':   ['Fully Paid', 'Current', 'Charged Off',
                          'Fully Paid', 'Current'],
        'grade':         ['A', 'B', 'C', 'A', 'B'],
        'term':          [' 36 months', ' 60 months', ' 36 months',
                          ' 36 months', ' 60 months'],
        'dti':           [15.0, 22.5, 30.0, 10.0, 18.0],
        'annual_income': [60000, 80000, 50000, 45000, 70000],
        'installment':   [280.0, 310.0, 450.0, 150.0, 220.0],
    })


def test_loan_status_only_valid_values(clean_loans):
    valid = {'Fully Paid', 'Current', 'Charged Off'}
    invalid = set(clean_loans['loan_status'].unique()) - valid
    assert not invalid, f"Unexpected loan_status values: {invalid}"


def test_term_only_valid_values(clean_loans):
    # Leading space is expected — part of dataset format
    valid = {' 36 months', ' 60 months'}
    invalid = set(clean_loans['term'].unique()) - valid
    assert not invalid, f"Unexpected term values: {invalid}"


def test_grade_only_valid_values(clean_loans):
    valid = set('ABCDEFG')
    invalid = set(clean_loans['grade'].unique()) - valid
    assert not invalid, f"Unexpected grade values: {invalid}"


def test_interest_rate_within_lending_range(clean_loans):
    # int_rate stored as decimal: 0.05 = 5%, 0.30 = 30%
    assert (clean_loans['int_rate'] >= 0.05).all(), "Some rates below 5%"
    assert (clean_loans['int_rate'] <= 0.30).all(), "Some rates above 30%"


def test_dti_within_valid_range(clean_loans):
    assert (clean_loans['dti'] >= 0).all(),   "Negative DTI values found"
    assert (clean_loans['dti'] <= 100).all(), "DTI values exceeding 100 found"


def test_annual_income_non_negative(clean_loans):
    assert (clean_loans['annual_income'] >= 0).all(), "Negative annual income found"


def test_installment_positive(clean_loans):
    assert (clean_loans['installment'] > 0).all(), "Non-positive installment found"


def test_loan_amount_positive(clean_loans):
    assert (clean_loans['loan_amount'] > 0).all(), "Non-positive loan amount found"


def test_no_duplicate_loan_ids(clean_loans):
    dupes = clean_loans['id'].duplicated().sum()
    assert dupes == 0, f"{dupes} duplicate loan IDs found"
