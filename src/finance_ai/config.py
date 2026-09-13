"""Runtime configuration helpers for local env-driven settings."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def load_environment(env_file: str | Path | None = None) -> None:
    """Load project .env values from the repo root or the explicit path."""
    candidates: list[Path] = []
    if env_file is not None:
        candidates.append(Path(env_file))

    project_root = Path(__file__).resolve().parents[2]
    candidates.extend(
        [
            project_root / ".env",
            Path.cwd() / ".env",
            project_root / "config" / ".env",
        ]
    )

    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.expanduser().resolve(strict=False)
        if resolved in seen:
            continue
        seen.add(resolved)
        loaded = load_dotenv(dotenv_path=resolved, override=False)
        if loaded:
            return

    load_dotenv(override=False)


def get_database_path() -> str:
    """Return the configured SQLite DB path, defaulting to the local data store."""
    load_environment()
    return os.getenv("DATABASE_PATH", "data/processed/finance.db")


def get_default_currency() -> str:
    """Return the configured default currency."""
    load_environment()
    return os.getenv("DEFAULT_CURRENCY", "NOK")
