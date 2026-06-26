import pandas as pd
import pytest
from validation.data_quality import (
    check_nulls, check_duplicates, check_value_range,
    check_allowed_values, check_positive_loan_amount, check_installment_positive,
)


@pytest.fixture
def clean_df():
    # int_rate stored as decimal (0.0542 = 5.42%) — matches actual dataset format
    return pd.DataFrame({
        'id':           [1, 2, 3, 4, 5],
        'loan_amount':  [10000, 15000, 20000, 5000, 8000],
        'int_rate':     [0.075, 0.120, 0.185, 0.090, 0.150],
        'loan_status':  ['Fully Paid', 'Current', 'Charged Off',
                         'Fully Paid', 'Current'],
        'grade':        ['A', 'B', 'C', 'A', 'B'],
        'term':         [' 36 months', ' 60 months', ' 36 months',
                         ' 36 months', ' 60 months'],
        'dti':          [15.0, 22.5, 30.0, 10.0, 18.0],
        'issue_date':   ['11-02-2021', '11-03-2021', '11-04-2021',
                         '11-05-2021', '11-06-2021'],
        'annual_income': [60000, 80000, 50000, 45000, 70000],
        'installment':  [280.0, 310.0, 450.0, 150.0, 220.0],
    })


# --- Null checks ---

def test_no_nulls_on_clean_data(clean_df):
    result = check_nulls(clean_df, ['loan_amount', 'int_rate', 'loan_status'])
    assert result.status == "PASS"

def test_null_check_detects_missing_values():
    df = pd.DataFrame({'loan_amount': [1000, None], 'int_rate': [0.10, 0.12]})
    result = check_nulls(df, ['loan_amount', 'int_rate'])
    assert result.status == "FAIL"
    assert result.failed_count == 1


# --- Duplicate checks ---

def test_no_duplicates_on_clean_data(clean_df):
    result = check_duplicates(clean_df, 'id')
    assert result.status == "PASS"

def test_duplicate_ids_detected():
    df = pd.DataFrame({'id': [1, 1, 2, 3]})
    result = check_duplicates(df, 'id')
    assert result.status == "FAIL"
    assert result.failed_count == 1


# --- Range checks (int_rate as decimal) ---

def test_interest_rate_valid_range(clean_df):
    result = check_value_range(clean_df, 'int_rate', 0.05, 0.30)
    assert result.status == "PASS"

def test_interest_rate_out_of_range_detected():
    df = pd.DataFrame({'int_rate': [0.075, 0.35, 0.02, 0.120]})
    result = check_value_range(df, 'int_rate', 0.05, 0.30)
    assert result.status == "FAIL"
    assert result.failed_count == 2

def test_dti_valid_range(clean_df):
    result = check_value_range(clean_df, 'dti', 0.0, 100.0)
    assert result.status == "PASS"


# --- Allowed values ---

def test_loan_status_valid_values(clean_df):
    result = check_allowed_values(
        clean_df, 'loan_status', ['Fully Paid', 'Current', 'Charged Off']
    )
    assert result.status == "PASS"

def test_invalid_loan_status_detected():
    df = pd.DataFrame({'loan_status': ['Fully Paid', 'UNKNOWN', 'Current']})
    result = check_allowed_values(
        df, 'loan_status', ['Fully Paid', 'Current', 'Charged Off']
    )
    assert result.status == "FAIL"
    assert result.failed_count == 1

def test_term_valid_values_with_leading_space(clean_df):
    # Dataset stores terms with a leading space: ' 36 months'
    result = check_allowed_values(clean_df, 'term', [' 36 months', ' 60 months'])
    assert result.status == "PASS"


# --- Business rules ---

def test_positive_loan_amount_valid(clean_df):
    result = check_positive_loan_amount(clean_df)
    assert result.status == "PASS"

def test_non_positive_loan_amount_detected():
    df = pd.DataFrame({'loan_amount': [10000, 0, -500]})
    result = check_positive_loan_amount(df)
    assert result.status == "FAIL"
    assert result.failed_count == 2

def test_installment_positive_valid(clean_df):
    result = check_installment_positive(clean_df)
    assert result.status == "PASS"

def test_non_positive_installment_detected():
    df = pd.DataFrame({'installment': [280.0, 0.0, -50.0]})
    result = check_installment_positive(df)
    assert result.status == "FAIL"
    assert result.failed_count == 2
