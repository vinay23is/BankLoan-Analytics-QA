# Dataset: financial_loan.csv

## Source
The `financial_loan.csv` dataset is a publicly available synthetic bank loan
dataset widely used in analytics projects on Kaggle and GitHub.

**Download from one of these sources:**
- Kaggle: search "bank loan analysis financial loan csv"
- GitHub mirror: https://github.com/aviwatgure/BANK_LOAN_DATASET_ANALYSIS

Place the downloaded file in this `data/` folder as `financial_loan.csv`.

## Key Fields Used in This Project

| Column         | Type    | Description                                      |
|----------------|---------|--------------------------------------------------|
| id             | int     | Unique loan identifier                           |
| loan_amount    | float   | Approved loan amount requested by borrower       |
| int_rate       | float   | Interest rate as decimal (0.1527 = 15.27%)       |
| installment    | float   | Monthly payment amount                           |
| grade          | string  | Risk grade: A (best) through G (highest risk)    |
| sub_grade      | string  | Sub-grade within grade band                      |
| loan_status    | string  | Fully Paid / Current / Charged Off               |
| issue_date     | string  | Date loan was issued                             |
| term           | string  | Loan term: ' 36 months' or ' 60 months'          |
| annual_income  | float   | Borrower annual income                           |
| dti            | float   | Debt-to-income ratio                             |
| purpose        | string  | Purpose of loan (debt_consolidation, etc.)       |
| addr_state     | string  | Borrower state                                   |
| total_payment  | float   | Total amount paid by borrower to date            |

## Notes
- Dataset is synthetic and safe for educational use
- ~38,000 rows
- No personally identifiable information
