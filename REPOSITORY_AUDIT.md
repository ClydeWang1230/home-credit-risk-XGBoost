# Repository Audit

## 1. Current Repository Overview

This repository is an existing Home Credit Risk XGBoost project that appears to be evolving from a Kaggle-style modeling prototype into a more professional credit risk analytics and AI-assisted decision support portfolio project.

Current top-level folders and files:

- `.git/`: Git repository metadata. This should remain untouched except through normal version control operations.
- `images-visualization/`: Existing visualization assets, likely charts, plots, screenshots, or images generated during analysis and modeling.
- `notebooks/`: Exploratory notebooks for data understanding, feature exploration, modeling experiments, and prototype analysis.
- `outputs/`: Generated project outputs, likely including model artifacts, prediction files, intermediate results, metrics, or exported analysis results.
- `sql_queries/`: SQL query files used for data extraction, feature generation, validation, or analytics workflows.
- `src/`: Formal source code directory for reusable project logic, such as data processing, feature engineering, modeling, configuration, or utility modules.
- `env.example`: Example environment variable file. This likely documents required local configuration such as paths, credentials, database settings, or Azure-related variables.
- `main.py`: Main pipeline entry point. It likely orchestrates data loading, feature processing, model training, prediction, and output generation.
- `PROJECT_BLUEPRINT.md`: Higher-level project blueprint describing goals, architecture, intended capabilities, and portfolio direction.
- `PROJECT_ROADMAP.md`: Roadmap document describing planned phases, milestones, and future improvements.
- `README.md`: Primary project documentation for setup, usage, project purpose, and repository orientation.
- `requirements.txt`: Python dependency list required to run the project.
- `weekly_roadmap.csv`: Planning artifact that likely tracks weekly tasks, phases, or implementation milestones.

## 2. Existing Useful Assets

The current repository already contains useful assets that should be preserved during any refactor unless they are reviewed and deliberately replaced.

Assets to preserve:

- `notebooks/`: Keep exploratory analysis and modeling notebooks. These are valuable for explaining project evolution, validating assumptions, and preserving experimentation history.
- `sql_queries/`: Preserve SQL queries because they may encode important business logic, feature definitions, joins, filters, or source-system assumptions.
- `src/`: Preserve existing source modules, especially any working feature engineering, data loading, model training, configuration, Azure integration, or utility code.
- `main.py`: Preserve the current runnable orchestration entry point until replacement responsibilities are clearly defined and tested.
- `images-visualization/`: Preserve visualizations and image assets that may support the README, reports, presentations, or portfolio narrative.
- `outputs/`: Preserve existing generated outputs until their contents are reviewed. They may include useful predictions, metrics, model artifacts, or examples of the current pipeline behavior.
- `README.md`: Preserve as the current user-facing documentation baseline.
- `requirements.txt`: Preserve as the current dependency reference before cleaning or restructuring it.
- `env.example`: Preserve as the initial configuration template, especially if it includes Azure, database, storage, or local path settings.
- `PROJECT_BLUEPRINT.md`: Preserve as the strategic architecture and project intent document.
- `PROJECT_ROADMAP.md`: Preserve as the implementation planning document.
- `weekly_roadmap.csv`: Preserve as a detailed planning tracker and timeline artifact.

## 3. Current Issues

The current repository appears to be in a useful but early-stage project maturity state. The main issues are structural clarity, pipeline modularity, and professional analytics output organization.

Potential current issues:

- Folder responsibilities may not yet be fully clear, especially the boundary between exploratory notebooks, formal source code, generated outputs, SQL assets, and visual report assets.
- `main.py` may be carrying too much orchestration logic if it directly handles data loading, feature engineering, training, prediction, evaluation, and output writing.
- Evaluation and scoring responsibilities may be incomplete or not yet separated into formal modules.
- Risk banding, scorecard-style interpretation, approval recommendation logic, or adverse-action style explanations may not yet exist as dedicated scoring logic.
- Output structure may be limited if predictions, model metrics, charts, reports, and artifacts are all stored together without clear subfolders.
- Documentation is likely still in an early transition state from prototype notes toward professional setup, architecture, and usage documentation.
- The project may still reflect Kaggle-style experimentation patterns, where outputs are generated mainly for modeling experiments rather than for professional credit risk analytics review.
- Visualizations may be stored in `images-visualization/`, which is understandable for a prototype but may eventually fit better under a reporting-oriented structure.
- SQL assets are currently in `sql_queries/`, which is descriptive but may eventually be simplified to `sql/` if the repository adopts a more standard analytics project layout.

## 4. Recommended Target Structure for V1.1

The V1.1 target should make the project easier to run, explain, test, and extend while preserving the current working assets. The repository should avoid creating empty folders or speculative modules before they are needed.

Recommended near-term structure:

```text
home-credit-risk-XGBoost/
  README.md
  requirements.txt
  env.example
  main.py
  PROJECT_BLUEPRINT.md
  PROJECT_ROADMAP.md
  REPOSITORY_AUDIT.md
  weekly_roadmap.csv
  notebooks/
  src/
  sql_queries/
  outputs/
  images-visualization/
```

Needed immediately:

- `src/`: Keep as the formal source code directory for reusable pipeline logic.
- `notebooks/`: Keep for exploratory analysis, experimentation, and prototype validation.
- `sql_queries/`: Keep for now to avoid unnecessary churn. Consider renaming to `sql/` later after confirming all references and documentation.
- `outputs/`: Keep for existing generated artifacts. Later, split into clearer subfolders only when the pipeline writes those assets consistently.
- `images-visualization/`: Keep for now. Consider migrating to `reports/figures/` later when a reporting structure is introduced.
- `main.py`: Keep as the current entry point until source modules have clear responsibilities.
- `requirements.txt`, `env.example`, and README/project planning documents: Keep and refine gradually.

Possible future structure after V1.1 stabilizes:

```text
home-credit-risk-XGBoost/
  README.md
  requirements.txt
  env.example
  main.py
  notebooks/
  src/
    data/
    features/
    models/
    evaluation.py
    scoring.py
    config.py
    utils.py
  sql/
  outputs/
    predictions/
    metrics/
    reports/
  reports/
    figures/
```

Future additions to consider only when needed:

- `src/evaluation.py`: Add when model evaluation metrics, validation reporting, calibration checks, or comparison workflows are being implemented.
- `src/scoring.py`: Add when risk bands, decision thresholds, score interpretations, or business-facing scoring logic are being implemented.
- `outputs/predictions/`: Add when prediction files are generated as a stable output.
- `outputs/metrics/`: Add when model metrics are generated as a stable output.
- `outputs/reports/`: Add when reports or report-ready summaries are generated as a stable output.
- `reports/figures/`: Add when visualizations are organized for final reports, README assets, or portfolio presentation.
- `sql/`: Consider as a future rename from `sql_queries/`, but only after confirming that no code, notebooks, or documentation depend on the current folder name.

## 5. Refactoring Principles

- Preserve existing working code.
- Avoid deleting files before verifying their contents, purpose, and downstream references.
- Refactor gradually rather than attempting a full rewrite.
- Keep the pipeline runnable after each major change.
- Separate exploratory notebooks from production-style source code.
- Keep `src/` as the formal home for reusable source modules.
- Avoid moving files until imports, paths, documentation, and output expectations are understood.
- Do not add AI, RAG, chatbot, or decision-support layers before the core risk analytics pipeline is mature.
- Prefer meaningful structure over empty folders.
- Let new folders and modules appear when there is working code or generated output that belongs there.
- Preserve portfolio narrative assets, including blueprint, roadmap, visualizations, and documented planning artifacts.

## 6. Suggested Refactoring Order

1. Review and document current assets.
2. Confirm target folder structure.
3. Keep `src/` as the formal source code directory.
4. Clean `requirements.txt`.
5. Improve `env.example` and `.gitignore` if needed.
6. Refactor `main.py` only after module responsibilities are clear.
7. Later add `evaluation.py` and `scoring.py` when model evaluation and risk band logic are being implemented.
8. Later improve `outputs/` into predictions, metrics, and reports.
9. Update `README.md` after the structure becomes stable.

## 7. Immediate Next Step

The next action should be reviewing this audit and deciding which existing files should be preserved, renamed, migrated, or deleted. No code files, existing folders, or existing project assets should be modified until that review is complete.
