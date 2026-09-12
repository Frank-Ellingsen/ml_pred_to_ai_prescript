"""SQLite connection manager with WAL mode and robust error handling."""

from collections.abc import Generator
from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3

DEFAULT_DB_PATH = Path("data/processed/finance.db")


def get_db_path() -> Path | str:
    """Resolve the active database path from environment or default."""
    env_path = os.getenv("DATABASE_PATH")
    if env_path:
        return env_path
    return DEFAULT_DB_PATH


@contextmanager
def get_connection(db_path: Path | str | None = None) -> Generator[sqlite3.Connection, None, None]:
    """Provide a transactional SQLite connection with WAL mode and row factory."""
    target_path = db_path if db_path is not None else get_db_path()

    # Ensure parent directory exists for file-based DBs
    if isinstance(target_path, Path) or (isinstance(target_path, str) and target_path != ":memory:"):
        Path(target_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        str(target_path),
        timeout=10.0,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    )
    conn.row_factory = sqlite3.Row

    # Performance and integrity pragmas
    if str(target_path) != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 5000;")

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
