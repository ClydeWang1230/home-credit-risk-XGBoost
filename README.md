# home-credit-risk-XGBoost
It developed an XGBoost model for credit default prediction, achieving a validation AUC of 0.7626 after applying early stopping.

# Home Credit Default Risk Prediction

## Project Overview
- **Goal**: Predict if a loan applicant will default.
- **Data**: Home Credit dataset from Kaggle.
- **My Approach**: Built an XGBoost model with two new features from previous application data.

## Key Files
- `home_credit_xgboost.ipynb`: The main Python notebook with EDA, feature engineering, and model training.
- `submission.csv`: Final prediction file.
- `sql_queries/`: Feature extraction queries (⏳ in progress)
- `tableau_dashboard.png`: Risk visualization (⏳ in progress)

## Results
- **Public Leaderboard Score**: `0.74165`
- **Private Leaderboard Score**: `0.74439`

## Key Features Engineered
- `n_prev_refusals`: How many times a client was previously rejected.
- `avg_annuity_prev`: Client's average historical loan annuity.

## Tech Stack
- Python (pandas, XGBoost)
- SQL (for data extraction queries)
- Tableau (for visualization, see `/images` folder)

## Tableau Dashboard
![Annuity by Contract_status](images-visualization/Refusal-Default.png)
![Annuity by Contract_status](images-visualization/Status-Annuity.png)
*Visualization confirming that clients with more past refusals have higher default rates.*

## How to Run
1. Clone this repo.
2. Run the notebook in Kaggle or Jupyter.
