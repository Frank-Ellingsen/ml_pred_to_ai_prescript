# Project Finance AI

Project Finance AI is a Python-based finance analytics and forecasting platform that combines deterministic financial calculations, a local SQLite repository, ML forecasting, CrewAI-style workflow orchestration, and optional experiment tracking with MLflow.

The project is designed for project-controlling and financial-analysis scenarios where teams need to explain budget variance, forecast project cost behavior, and produce a consistent analysis narrative from structured domain data.

## Features

- Deterministic finance analysis flow and typed domain contracts
- SQLite-backed repository and seed data layer
- Forecasting model training with scikit-learn and joblib
- Optional MLflow experiment tracking for model runs and artifacts
- CLI commands for database setup, seeding, analysis execution, and model training
- Extensible Python package structure for tools, agents, ML feature engineering, and orchestration

## Project Structure

```text
.
├── src/finance_ai/
│   ├── agents/           # CrewAI agents and orchestration glue
│   ├── cli.py            # Command-line interface
│   ├── database/         # SQLite repository, schema, and seed data
│   ├── domain/           # Typed contracts for finance analysis
│   ├── ml/               # Forecasting and MLflow tracking helpers
│   ├── orchestration/    # Flow orchestration and analysis workflow
│   └── tools/            # Finance and forecasting tools
├── config/               # Agent and workflow configuration
├── data/                 # Raw, processed, and feedback data
├── knowledge/            # Policies, catalog, and runbook knowledge sources
├── artifacts/            # Generated artifacts and model outputs
└── tests/                # Smoke and regression tests
```

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install the project dependencies
pip install -r requirements.txt
pip install -e .

# 3. Copy the sample environment file
copy .env.example .env

# 4. Initialize the SQLite schema
finance-init-db

# 5. Seed the repository with sample data
finance-seed-db

# 6. Run the analysis flow
finance-run-analysis

# 7. Train the forecasting model and save the artifact
finance-train
```

## Local Setup

Create a virtual environment and install the project dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

If you want to use the local MLflow file backend, copy the provided environment example and configure the tracking URI:

```bash
copy .env.example .env
```

Available environment variables include:

```text
MLFLOW_TRACKING_URI=file:///artifacts/mlruns
MLFLOW_EXPERIMENT_NAME=finance_ai
DATABASE_PATH=data/processed/finance.db
DEFAULT_CURRENCY=NOK
VARIANCE_THRESHOLD_PERCENT=0.05
```

## CLI Commands

The package exposes the following project scripts through `pyproject.toml`:

```bash
finance-init-db
finance-seed-db
finance-run-analysis
finance-train
```

The CLI also exposes a runtime-status command to inspect the active database and environment settings:

```bash
python -m finance_ai.cli status
```

You can also invoke the CLI module directly:

```bash
python -m finance_ai.cli init-database
python -m finance_ai.cli seed-database
python -m finance_ai.cli status
python -m finance_ai.cli run-analysis
python -m finance_ai.cli train-models
```

Project runtime values are loaded from `.env` automatically when present, so you can keep local configuration in the project root without hardcoding secrets or paths.

## Training Workflow

The current training command fits the `ProjectCostForecaster` and saves the artifact to:

```text
artifacts/models/project_cost_forecaster.joblib
```

The tracking helper in `finance_ai.ml.mlflow_tracking` logs model metadata and metric information when MLflow is installed, while keeping the existing artifact save path as the primary serialization record.

## Testing

Run the project test suite with:

```bash
python -m pytest
```

## License

MIT
