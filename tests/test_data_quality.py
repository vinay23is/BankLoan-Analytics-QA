import pandas as pd
import pytest
from validation.data_quality import (
    check_nulls, check_duplicates, check_value_range,
    check_allowed_values, check_funded_lte_loan, check_positive_amounts,
)


@pytest.fixture
def clean_df():
    return pd.DataFrame({
        'id':            [1, 2, 3, 4, 5],
        'loan_amount':   [10000, 15000, 20000, 5000, 8000],
        'funded_amount': [9500,  14000, 19000, 5000, 7500],
        'int_rate':      [7.5,   12.0,  18.5,  9.0, 15.0],
        'loan_status':   ['Fully Paid', 'Current', 'Charged Off',
                          'Fully Paid', 'Current'],
        'grade':         ['A', 'B', 'C', 'A', 'B'],
        'dti':           [15.0, 22.5, 30.0, 10.0, 18.0],
        'issue_date':    ['2022-01-01', '2022-02-01', '2022-03-01',
                          '2022-04-01', '2022-05-01'],
        'annual_income': [60000, 80000, 50000, 45000, 70000],
    })


# --- Null checks ---

def test_no_nulls_on_clean_data(clean_df):
    result = check_nulls(clean_df, ['loan_amount', 'funded_amount', 'int_rate'])
    assert result.status == "PASS"

def test_null_check_detects_missing_values():
    df = pd.DataFrame({'loan_amount': [1000, None], 'funded_amount': [900, 800]})
    result = check_nulls(df, ['loan_amount', 'funded_amount'])
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


# --- Range checks ---

def test_interest_rate_valid_range(clean_df):
    result = check_value_range(clean_df, 'int_rate', 5.0, 30.0)
    assert result.status == "PASS"

def test_interest_rate_out_of_range_detected():
    df = pd.DataFrame({'int_rate': [7.5, 35.0, 2.0, 12.0]})
    result = check_value_range(df, 'int_rate', 5.0, 30.0)
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


# --- Business rules ---

def test_funded_does_not_exceed_loan(clean_df):
    result = check_funded_lte_loan(clean_df)
    assert result.status == "PASS"

def test_funded_exceeding_loan_detected():
    df = pd.DataFrame({
        'loan_amount':   [10000, 5000],
        'funded_amount': [10000, 6000],   # second row violates rule
    })
    result = check_funded_lte_loan(df)
    assert result.status == "FAIL"
    assert result.failed_count == 1

def test_positive_amounts_valid(clean_df):
    result = check_positive_amounts(clean_df)
    assert result.status == "PASS"

def test_non_positive_amounts_detected():
    df = pd.DataFrame({'loan_amount': [10000, 0], 'funded_amount': [9000, 8000]})
    result = check_positive_amounts(df)
    assert result.status == "FAIL"
