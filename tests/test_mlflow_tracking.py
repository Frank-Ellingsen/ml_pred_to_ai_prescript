import os
from pathlib import Path


def test_log_training_run_accepts_file_backend(tmp_path):
    """Smoke test for the MLflow integration helper before the training hook is added."""
    from finance_ai.ml.mlflow_tracking import log_training_run

    artifact_path = tmp_path / "project_cost_forecaster.joblib"
    artifact_path.write_text("placeholder-model", encoding="utf-8")

    tracking_uri = f"file:///{tmp_path / 'mlruns'}"
    tracking_uri = tracking_uri.replace("\\", "/")
    run_info = log_training_run(
        model_name="project_cost_forecaster",
        model_version="v2026.1",
        metric_name="residual_std",
        metric_value=0.5,
        artifact_path=artifact_path,
        tracking_uri=tracking_uri,
        experiment_name="test-finance-ai",
    )

    assert run_info is not None
    assert Path(run_info["artifact_path"]).exists()
    assert run_info["tracking_uri"].startswith("sqlite:///")


def test_log_training_run_sets_file_store_allowance(tmp_path, monkeypatch):
    """Regression test: the local file-backed MLflow URI must opt into the backend allowance that MLflow 2.22 expects."""
    from finance_ai.ml.mlflow_tracking import log_training_run

    monkeypatch.delenv("MLFLOW_ALLOW_FILE_STORE", raising=False)
    artifact_path = tmp_path / "project_cost_forecaster.joblib"
    artifact_path.write_text("placeholder-model", encoding="utf-8")

    tracking_uri = f"file:///{tmp_path / 'mlruns'}"
    tracking_uri = tracking_uri.replace("\\", "/")
    run_info = log_training_run(
        model_name="project_cost_forecaster",
        model_version="v2026.1",
        metric_name="residual_std",
        metric_value=0.5,
        artifact_path=artifact_path,
        tracking_uri=tracking_uri,
        experiment_name="test-finance-ai",
    )

    assert run_info is not None
    assert run_info["tracking_uri"].startswith("sqlite:///")
    assert os.getenv("MLFLOW_ALLOW_FILE_STORE", "").lower() == "true"
