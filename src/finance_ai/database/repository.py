"""Typed data access repository for SQLite persistence."""

import sqlite3
from contextlib import suppress
from decimal import Decimal
from pathlib import Path
from typing import Any

from finance_ai.database.connection import get_connection

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init_db(db_path: Path | str | None = None) -> None:
    """Initialize database tables and full-text index from schema.sql."""
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        schema_sql = f.read()

    with get_connection(db_path) as conn:
        conn.executescript(schema_sql)


def get_actuals(entity_id: str, db_path: Path | str | None = None) -> list[dict[str, Any]]:
    """Retrieve historical actuals for an entity ordered chronologically."""
    sql = """
    SELECT
        entity_id,
        period,
        revenue,
        cost,
        customers,
        units,
        currency,
        data_as_of
    FROM actuals
    WHERE entity_id = ?
    ORDER BY period ASC
    """
    with get_connection(db_path) as conn:
        rows = conn.execute(sql, (entity_id,)).fetchall()

    return [
        {
            "entity_id": row["entity_id"],
            "period": row["period"],
            "revenue": Decimal(str(row["revenue"])),
            "cost": Decimal(str(row["cost"])),
            "customers": row["customers"],
            "units": row["units"],
            "currency": row["currency"],
            "data_as_of": row["data_as_of"],
        }
        for row in rows
    ]


def get_budget(
    entity_id: str,
    metric: str,
    period: str,
    db_path: Path | str | None = None,
) -> dict[str, Any] | None:
    """Retrieve the latest approved budget for a given entity, metric, and period."""
    sql = """
    SELECT
        entity_id,
        period,
        metric,
        amount,
        currency,
        budget_version
    FROM budgets
    WHERE
        entity_id = ?
        AND metric = ?
        AND period = ?
    ORDER BY budget_version DESC
    LIMIT 1
    """
    with get_connection(db_path) as conn:
        row = conn.execute(sql, (entity_id, metric, period)).fetchone()

    if row is None:
        return None

    return {
        "entity_id": row["entity_id"],
        "period": row["period"],
        "metric": row["metric"],
        "amount": Decimal(str(row["amount"])),
        "currency": row["currency"],
        "budget_version": row["budget_version"],
    }


def get_latest_forecast(
    entity_id: str,
    metric: str,
    db_path: Path | str | None = None,
) -> dict[str, Any] | None:
    """Retrieve the latest authoritative predictive ML forecast with prediction intervals."""
    sql = """
    SELECT
        forecast_id,
        entity_id,
        metric,
        period,
        point_estimate,
        lower,
        upper,
        confidence,
        model_name,
        model_version,
        forecast_as_of,
        data_as_of
    FROM forecasts
    WHERE entity_id = ? AND metric = ?
    ORDER BY forecast_as_of DESC, period ASC
    """
    with get_connection(db_path) as conn:
        rows = conn.execute(sql, (entity_id, metric)).fetchall()

    if not rows:
        return None

    first = rows[0]
    forecast_points = []
    for r in rows:
        forecast_points.append(
            {
                "period": r["period"],
                "point_estimate": Decimal(str(r["point_estimate"])),
                "lower": Decimal(str(r["lower"])) if r["lower"] is not None else None,
                "upper": Decimal(str(r["upper"])) if r["upper"] is not None else None,
                "confidence": r["confidence"],
            }
        )

    return {
        "entity_id": first["entity_id"],
        "metric": first["metric"],
        "model_name": first["model_name"],
        "model_version": first["model_version"],
        "forecast_as_of": first["forecast_as_of"],
        "data_as_of": first["data_as_of"],
        "forecast": forecast_points,
    }


def search_documents(
    query: str,
    limit: int = 5,
    db_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Search approved documents and runbooks using FTS5 with fallback to LIKE search."""
    # Try FTS5 first
    clean_query = "".join(c for c in query if c.isalnum() or c.isspace()).strip()
    if not clean_query:
        clean_query = query.strip()

    fts_sql = """
    SELECT
        d.document_id,
        d.title,
        d.document_type,
        d.period,
        d.version,
        d.source_uri,
        d.content
    FROM documents_fts f
    JOIN documents d ON d.document_id = f.document_id
    WHERE documents_fts MATCH ?
    LIMIT ?
    """
    like_sql = """
    SELECT
        document_id,
        title,
        document_type,
        period,
        version,
        source_uri,
        content
    FROM documents
    WHERE title LIKE ? OR content LIKE ?
    LIMIT ?
    """

    with get_connection(db_path) as conn:
        try:
            rows = conn.execute(fts_sql, (f"{clean_query}*", limit)).fetchall()
            if rows:
                return [dict(r) for r in rows]
        except sqlite3.OperationalError:
            pass

        # Fallback to standard LIKE
        like_pattern = f"%{clean_query}%"
        rows = conn.execute(like_sql, (like_pattern, like_pattern, limit)).fetchall()
        return [dict(r) for r in rows]


def insert_actuals(rows: list[dict[str, Any]], db_path: Path | str | None = None) -> None:
    """Insert or replace historical actuals."""
    sql = """
    INSERT OR REPLACE INTO actuals (
        entity_id, period, revenue, cost, customers, units, currency, data_as_of
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    with get_connection(db_path) as conn:
        conn.executemany(
            sql,
            [
                (
                    r["entity_id"],
                    r["period"],
                    float(r["revenue"]),
                    float(r["cost"]),
                    r.get("customers", 0),
                    r.get("units", 0),
                    r.get("currency", "NOK"),
                    r["data_as_of"],
                )
                for r in rows
            ],
        )


def insert_budget(rows: list[dict[str, Any]], db_path: Path | str | None = None) -> None:
    """Insert or replace budget records."""
    sql = """
    INSERT OR REPLACE INTO budgets (
        entity_id, period, metric, amount, currency, budget_version
    ) VALUES (?, ?, ?, ?, ?, ?)
    """
    with get_connection(db_path) as conn:
        conn.executemany(
            sql,
            [
                (
                    r["entity_id"],
                    r["period"],
                    r["metric"],
                    float(r["amount"]),
                    r.get("currency", "NOK"),
                    r["budget_version"],
                )
                for r in rows
            ],
        )


def insert_forecast(rows: list[dict[str, Any]], db_path: Path | str | None = None) -> None:
    """Insert or replace forecast predictions."""
    sql = """
    INSERT OR REPLACE INTO forecasts (
        forecast_id, entity_id, metric, period, point_estimate,
        lower, upper, confidence, model_name, model_version, forecast_as_of, data_as_of
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    with get_connection(db_path) as conn:
        conn.executemany(
            sql,
            [
                (
                    r["forecast_id"],
                    r["entity_id"],
                    r["metric"],
                    r["period"],
                    float(r["point_estimate"]),
                    float(r["lower"]) if r.get("lower") is not None else None,
                    float(r["upper"]) if r.get("upper") is not None else None,
                    r.get("confidence", 0.90),
                    r["model_name"],
                    r["model_version"],
                    r["forecast_as_of"],
                    r["data_as_of"],
                )
                for r in rows
            ],
        )


def insert_document(doc: dict[str, Any], db_path: Path | str | None = None) -> None:
    """Insert document and index it in FTS5."""
    doc_sql = """
    INSERT OR REPLACE INTO documents (
        document_id, title, document_type, period, version, source_uri, content
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    fts_sql = """
    INSERT INTO documents_fts (document_id, title, content)
    VALUES (?, ?, ?)
    """
    with get_connection(db_path) as conn:
        conn.execute(
            doc_sql,
            (
                doc["document_id"],
                doc["title"],
                doc["document_type"],
                doc.get("period"),
                doc.get("version", "1.0"),
                doc.get("source_uri"),
                doc["content"],
            ),
        )
        with suppress(sqlite3.OperationalError):
            conn.execute(fts_sql, (doc["document_id"], doc["title"], doc["content"]))


def insert_feedback(feedback: dict[str, Any], db_path: Path | str | None = None) -> None:
    """Insert human feedback and decision review."""
    sql = """
    INSERT OR REPLACE INTO feedback (
        feedback_id, analysis_id, decision, actual_outcome, reviewer, timestamp, comments
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    with get_connection(db_path) as conn:
        conn.execute(
            sql,
            (
                feedback["feedback_id"],
                feedback["analysis_id"],
                feedback["decision"],
                feedback.get("actual_outcome"),
                feedback["reviewer"],
                feedback["timestamp"],
                feedback.get("comments"),
            ),
        )
