import pandas as pd
import sqlite3
from typing import Dict

# Definitions shown in reports and interview explanations
KPI_DEFINITIONS = {
    'good_loan_rate_pct':  "% of loans that are Fully Paid or Current",
    'bad_loan_rate_pct':   "% of loans that are Charged Off (NPA proxy)",
    'avg_interest_rate':   "Average interest rate across all loans",
    'avg_funded_amount':   "Average funded amount per loan",
    'total_funded_amount': "Total capital deployed across all loans",
    'total_applications':  "Total number of loan applications in dataset",
}


def compute_kpis_pandas(df: pd.DataFrame) -> Dict[str, float]:
    """Reference KPI calculation using pandas."""
    total = len(df)
    good  = df[df['loan_status'].isin(['Fully Paid', 'Current'])].shape[0]
    bad   = df[df['loan_status'] == 'Charged Off'].shape[0]
    return {
        'good_loan_rate_pct':  round(good / total * 100, 2),
        'bad_loan_rate_pct':   round(bad  / total * 100, 2),
        'avg_interest_rate':   round(float(df['int_rate'].mean()), 4),
        'avg_funded_amount':   round(float(df['funded_amount'].mean()), 2),
        'total_funded_amount': round(float(df['funded_amount'].sum()), 2),
        'total_applications':  total,
    }


def compute_kpis_sql(df: pd.DataFrame) -> Dict[str, float]:
    """Same KPIs computed via SQL on in-memory SQLite.

    In production this side would be replaced by a Power BI REST API
    export or a direct query against the reporting database.
    """
    conn = sqlite3.connect(':memory:')
    df.to_sql('loans', conn, index=False, if_exists='replace')
    query = """
        SELECT
            ROUND(
                CAST(SUM(CASE WHEN loan_status IN ('Fully Paid','Current')
                              THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2
            ) AS good_loan_rate_pct,
            ROUND(
                CAST(SUM(CASE WHEN loan_status = 'Charged Off'
                              THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2
            ) AS bad_loan_rate_pct,
            ROUND(AVG(int_rate), 4)        AS avg_interest_rate,
            ROUND(AVG(funded_amount), 2)   AS avg_funded_amount,
            ROUND(SUM(funded_amount), 2)   AS total_funded_amount,
            COUNT(*)                       AS total_applications
        FROM loans
    """
    result = pd.read_sql_query(query, conn)
    conn.close()
    return {k: float(v) for k, v in result.iloc[0].to_dict().items()}
