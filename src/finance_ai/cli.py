"""Command Line Interface for Project Finance AI."""

import argparse
import json
import sys

from finance_ai.database.repository import init_db
from finance_ai.database.seed_data import seed_database as seed_db_fn
from finance_ai.orchestration.analysis_flow import FinancialAnalysisFlow


def init_database() -> None:
    """Initialize the SQLite database schema."""
    print("Initializing SQLite database schema...")
    init_db()
    print("Database schema initialized successfully.")


def seed_database() -> None:
    """Seed the SQLite database with baseline data."""
    print("Seeding SQLite database with project controlling data (NOK)...")
    seed_db_fn()
    print("Database seeded successfully.")


def run_analysis(
    question: str = "Why is revenue below budget and what should I investigate?",
    entity_id: str = "Project-Vessel-2026",
    period: str = "2025-Q2",
    currency: str = "NOK",
) -> None:
    """Execute the full FinancialAnalysisFlow."""
    print(f"Starting analysis for entity='{entity_id}', period='{period}'...")
    flow = FinancialAnalysisFlow()
    flow.state.question = question
    flow.state.entity_id = entity_id
    flow.state.period = period
    flow.state.currency = currency

    result = flow.kickoff()
    print("\n--- Final Analysis Result ---")
    print(result.model_dump_json(indent=2))


def train_models() -> None:
    """Train predictive forecasting models and save artifacts, optionally logging to MLflow."""
    import numpy as np
    from finance_ai.ml.forecaster import ProjectCostForecaster
    from finance_ai.ml.mlflow_tracking import log_training_run

    print("Training predictive project cost forecaster...")
    # Synthetic time-series features: [step, lag_1, rolling_mean_2]
    X_train = np.array([
        [0, 31_000_000, 31_000_000],
        [1, 31_000_000, 32_750_000],
        [2, 34_500_000, 35_850_000],
        [3, 37_200_000, 39_600_000],
    ])
    y_train = np.array([31_000_000, 34_500_000, 37_200_000, 42_000_000])

    forecaster = ProjectCostForecaster(model_version="v2026.1")
    forecaster.fit(X_train, y_train)

    artifact_path = "artifacts/models/project_cost_forecaster.joblib"
    forecaster.save(artifact_path)

    tracking_payload = log_training_run(
        model_name="project_cost_forecaster",
        model_version="v2026.1",
        metric_name="residual_std",
        metric_value=float(forecaster.residual_std),
        artifact_path=artifact_path,
    )

    print(f"Model trained and saved to {artifact_path}")
    if tracking_payload.get("mlflow_available"):
        print(f"MLflow run recorded: {tracking_payload.get('run_id')}")
    else:
        print("MLflow package unavailable; tracking payload emitted without remote run creation.")


def main() -> None:
    """CLI dispatcher."""
    parser = argparse.ArgumentParser(description="Project Finance AI CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("init-database", help="Initialize SQLite tables")
    subparsers.add_parser("seed-database", help="Seed database with sample data")

    analyze_parser = subparsers.add_parser("run-analysis", help="Run financial analysis flow")
    analyze_parser.add_argument("--question", default="Why is revenue below budget and what should I investigate?")
    analyze_parser.add_argument("--entity", default="Project-Vessel-2026")
    analyze_parser.add_argument("--period", default="2025-Q2")
    analyze_parser.add_argument("--currency", default="NOK")

    subparsers.add_parser("train-models", help="Train predictive ML models")

    args = parser.parse_args()

    if args.command == "init-database":
        init_database()
    elif args.command == "seed-database":
        seed_database()
    elif args.command == "run-analysis":
        run_analysis(
            question=args.question,
            entity_id=args.entity,
            period=args.period,
            currency=args.currency,
        )
    elif args.command == "train-models":
        train_models()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
