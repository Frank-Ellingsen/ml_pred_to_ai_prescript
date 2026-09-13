import os

from finance_ai.cli import status
from finance_ai.config import load_environment


def test_load_environment_reads_explicit_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_PATH=data/custom.db\nDEFAULT_CURRENCY=USD\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    load_environment(env_file)

    assert os.getenv("DATABASE_PATH") == "data/custom.db"
    assert os.getenv("DEFAULT_CURRENCY") == "USD"
    assert env_file.exists()


def test_status_reports_runtime_configuration(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "finance.db"))
    monkeypatch.setenv("DEFAULT_CURRENCY", "USD")
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "sqlite:///artifacts/test.db")

    status()

    output = capsys.readouterr().out
    assert "Project Finance AI status" in output
    assert "database_path=" in output
    assert "default_currency=USD" in output
    assert "mlflow_tracking_uri=sqlite:///artifacts/test.db" in output
