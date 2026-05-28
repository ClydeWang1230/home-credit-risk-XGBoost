# Project Roadmap: Home Credit Risk XGBoost

This 8-week roadmap upgrades the existing Home Credit Risk XGBoost project from a Kaggle-style prototype into a professional portfolio project for fintech, banking analytics, risk analytics, and data science roles.

The project already includes dataset exploration, feature engineering, an XGBoost model with validation AUC around 0.76, SQL / Tableau / Azure Blob Storage elements, and early modular Python pipeline work. The roadmap focuses on refactoring, professionalizing, extending, and packaging the existing work rather than rebuilding the project from zero.

## Week 1: Project Positioning and Repository Audit

| Category | Details |
| --- | --- |
| Week | Week 1 |
| Main Goal | Clarify the project positioning, audit the current repository, and define the final portfolio scope. |
| Key Deliverables | Repository audit notes; list of completed assets; list of refactoring needs; `PROJECT_BLUEPRINT.md`; finalized project scope and success criteria. |
| Success Criteria | The project has a clear professional identity, target audience, business problem, architecture direction, and realistic upgrade scope. |
| Notes | Focus on understanding what already exists before changing the codebase. The goal is to preserve useful existing work while identifying what needs to become more production-like. |

## Week 2: Engineering Cleanup and Reproducibility

| Category | Details |
| --- | --- |
| Week | Week 2 |
| Main Goal | Make the project easier to clone, run, and understand as a professional analytics repository. |
| Key Deliverables | Standardized folder structure; cleaned Python imports and modules; updated `requirements.txt`; runnable main pipeline; config files if needed; improved README run instructions. |
| Success Criteria | A reviewer can clone the repository, install dependencies, understand the folder structure, and run the main pipeline without guessing how the project works. |
| Notes | Prioritize reproducibility and clarity over adding new features. Keep the refactor close to the current pipeline so existing model work is not lost. |

## Week 3: Model Evaluation and Risk Interpretation

| Category | Details |
| --- | --- |
| Week | Week 3 |
| Main Goal | Strengthen model evaluation and translate model outputs into credit risk language. |
| Key Deliverables | ROC-AUC, precision, recall, confusion matrix, and KS statistic; Logistic Regression baseline; XGBoost comparison; Low / Medium / High risk band logic; business-language model interpretation. |
| Success Criteria | The model is evaluated with both technical metrics and business-oriented interpretation, and the project explains why the model is useful for credit risk decision support. |
| Notes | The existing XGBoost validation AUC around 0.76 should be treated as a foundation. The upgrade should show stronger evaluation discipline, not just a higher score. |

## Week 4: SQL and Analytics Layer

| Category | Details |
| --- | --- |
| Week | Week 4 |
| Main Goal | Build a banking-style analytics layer that supports portfolio monitoring and risk reporting. |
| Key Deliverables | Analytical table design; SQL scripts for customer, loan, repayment, and risk features; portfolio-level risk analysis; default rate by customer segment; high-risk customer output table. |
| Success Criteria | The project includes SQL assets that show how raw and modeled data can be converted into reusable analytical tables for bank / fintech reporting. |
| Notes | This week should connect the project to data analyst, analytics engineer, and risk analyst expectations, not only machine learning expectations. |

## Week 5: Dashboard and Reporting Layer

| Category | Details |
| --- | --- |
| Week | Week 5 |
| Main Goal | Create a dashboard layer that communicates risk insights to business stakeholders. |
| Key Deliverables | Portfolio monitoring dashboard; risk band distribution view; default rate by segment; model performance view; high-risk customer list; dashboard screenshots added to README. |
| Success Criteria | The project can be reviewed visually through dashboard screenshots or a demo, and the reporting layer clearly connects model outputs to portfolio risk monitoring. |
| Notes | Keep the dashboard practical and analyst-oriented. It should feel like a working risk monitoring tool, not a decorative visualization exercise. |

## Week 6: AI-assisted Risk Review MVP

| Category | Details |
| --- | --- |
| Week | Week 6 |
| Main Goal | Add a simple AI-assisted layer that turns model outputs and risk drivers into analyst-style credit review summaries. |
| Key Deliverables | Simple credit policy document; AI assistant prototype; English credit risk review summaries; explanation logic connected to model outputs, risk drivers, and policy rules. |
| Success Criteria | A sample borrower can be scored, assigned a risk band, and explained through a clear analyst-style summary that references relevant risk factors. |
| Notes | Keep the MVP controlled and explainable. The AI layer should support analyst review rather than replace credit decision-making. |

## Week 7: End-to-end Integration

| Category | Details |
| --- | --- |
| Week | Week 7 |
| Main Goal | Connect the cleaned data workflow, model scoring, risk banding, dashboard outputs, and AI review into a coherent demo workflow. |
| Key Deliverables | Integrated pipeline flow; reproducible scoring outputs; sample inputs and outputs; dashboard-ready files; AI review examples; demo workflow documentation. |
| Success Criteria | The project can demonstrate an end-to-end journey from data preparation to model scoring, risk interpretation, portfolio reporting, and AI-assisted review. |
| Notes | This week is about making the pieces work together. The final result should feel like one platform concept rather than separate notebooks and scripts. |

## Week 8: Portfolio Polish and Interview Preparation

| Category | Details |
| --- | --- |
| Week | Week 8 |
| Main Goal | Package the project for GitHub, portfolio review, and job interviews. |
| Key Deliverables | Final README; architecture diagram; screenshots; project limitations and future improvements; 2-minute project pitch; 10-minute technical deep dive; interview Q&A. |
| Success Criteria | The repository is ready to share with recruiters, hiring managers, and interviewers, and the project story can be explained clearly at both business and technical levels. |
| Notes | The final polish should emphasize business impact, engineering maturity, analytical thinking, and communication. The project should be easy to evaluate quickly and credible enough for deeper technical discussion. |
