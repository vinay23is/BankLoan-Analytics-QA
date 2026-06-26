"""
Banking business rule tests.
Each test encodes one domain rule as an executable assertion.
This prevents silent regressions when upstream data transforms change.
"""
import pandas as pd
import pytest


@pytest.fixture
def clean_loans():
    return pd.DataFrame({
        'id':            [1, 2, 3, 4, 5],
        'loan_amount':   [10000, 15000, 20000, 5000, 8000],
        'funded_amount': [9500,  14000, 19000, 5000, 7500],
        'int_rate':      [7.5,   12.0,  18.5,  9.0, 15.0],
        'loan_status':   ['Fully Paid', 'Current', 'Charged Off',
                          'Fully Paid', 'Current'],
        'grade':         ['A', 'B', 'C', 'A', 'B'],
        'term':          ['36 months', '60 months', '36 months',
                          '36 months', '60 months'],
        'dti':           [15.0, 22.5, 30.0, 10.0, 18.0],
        'annual_income': [60000, 80000, 50000, 45000, 70000],
        'installment':   [280.0, 310.0, 450.0, 150.0, 220.0],
    })


def test_funded_amount_never_exceeds_loan_amount(clean_loans):
    violations = clean_loans[clean_loans['funded_amount'] > clean_loans['loan_amount']]
    assert len(violations) == 0, (
        f"{len(violations)} loans where funded_amount > loan_amount"
    )


def test_loan_status_only_valid_values(clean_loans):
    valid = {'Fully Paid', 'Current', 'Charged Off'}
    invalid = set(clean_loans['loan_status'].unique()) - valid
    assert not invalid, f"Unexpected loan_status values: {invalid}"


def test_term_only_valid_values(clean_loans):
    valid = {'36 months', '60 months'}
    invalid = set(clean_loans['term'].unique()) - valid
    assert not invalid, f"Unexpected term values: {invalid}"


def test_grade_only_valid_values(clean_loans):
    valid = set('ABCDEFG')
    invalid = set(clean_loans['grade'].unique()) - valid
    assert not invalid, f"Unexpected grade values: {invalid}"


def test_interest_rate_within_lending_range(clean_loans):
    assert (clean_loans['int_rate'] >= 5.0).all(), "Some interest rates below 5%"
    assert (clean_loans['int_rate'] <= 30.0).all(), "Some interest rates above 30%"


def test_dti_within_valid_range(clean_loans):
    assert (clean_loans['dti'] >= 0).all(), "Negative DTI values found"
    assert (clean_loans['dti'] <= 100).all(), "DTI values exceeding 100 found"


def test_annual_income_non_negative(clean_loans):
    assert (clean_loans['annual_income'] >= 0).all(), "Negative annual income found"


def test_installment_positive(clean_loans):
    assert (clean_loans['installment'] > 0).all(), "Non-positive installment found"


def test_no_duplicate_loan_ids(clean_loans):
    dupes = clean_loans['id'].duplicated().sum()
    assert dupes == 0, f"{dupes} duplicate loan IDs found"
