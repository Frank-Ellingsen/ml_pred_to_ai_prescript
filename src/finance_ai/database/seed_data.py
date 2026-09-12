"""Deterministic seed data for Project Controlling and Maritime Engineering (NOK)."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from finance_ai.database.repository import (
    init_db,
    insert_actuals,
    insert_budget,
    insert_document,
    insert_forecast,
)

ENTITY_ID = "Project-Vessel-2026"
CURRENCY = "NOK"


def seed_database(db_path: Path | str | None = None) -> None:
    """Populate SQLite database with realistic project controlling baseline data."""
    init_db(db_path)

    # 1. Historical Actuals (NOK)
    actuals = [
        {
            "entity_id": ENTITY_ID,
            "period": "2024-Q3",
            "revenue": 38_000_000,
            "cost": 31_000_000,
            "customers": 1,
            "units": 1,
            "currency": CURRENCY,
            "data_as_of": "2024-10-05T00:00:00Z",
        },
        {
            "entity_id": ENTITY_ID,
            "period": "2024-Q4",
            "revenue": 42_000_000,
            "cost": 34_500_000,
            "customers": 1,
            "units": 1,
            "currency": CURRENCY,
            "data_as_of": "2025-01-08T00:00:00Z",
        },
        {
            "entity_id": ENTITY_ID,
            "period": "2025-Q1",
            "revenue": 46_500_000,
            "cost": 37_200_000,
            "customers": 1,
            "units": 2,
            "currency": CURRENCY,
            "data_as_of": "2025-04-06T00:00:00Z",
        },
        {
            "entity_id": ENTITY_ID,
            "period": "2025-Q2",
            "revenue": 45_000_000,  # Below budget (50M) due to milestone certificate delay
            "cost": 42_000_000,     # Above budget (38M) due to propulsion system subcontractor surge
            "customers": 1,
            "units": 2,
            "currency": CURRENCY,
            "data_as_of": "2025-07-05T00:00:00Z",
        },
    ]
    insert_actuals(actuals, db_path)

    # 2. Approved Budgets (NOK)
    budgets = [
        {"entity_id": ENTITY_ID, "period": "2024-Q3", "metric": "revenue", "amount": 38_000_000, "currency": CURRENCY, "budget_version": "v1.0"},
        {"entity_id": ENTITY_ID, "period": "2024-Q3", "metric": "cost", "amount": 31_000_000, "currency": CURRENCY, "budget_version": "v1.0"},
        {"entity_id": ENTITY_ID, "period": "2024-Q4", "metric": "revenue", "amount": 42_000_000, "currency": CURRENCY, "budget_version": "v1.0"},
        {"entity_id": ENTITY_ID, "period": "2024-Q4", "metric": "cost", "amount": 34_000_000, "currency": CURRENCY, "budget_version": "v1.0"},
        {"entity_id": ENTITY_ID, "period": "2025-Q1", "metric": "revenue", "amount": 46_000_000, "currency": CURRENCY, "budget_version": "v1.0"},
        {"entity_id": ENTITY_ID, "period": "2025-Q1", "metric": "cost", "amount": 37_000_000, "currency": CURRENCY, "budget_version": "v1.0"},
        {"entity_id": ENTITY_ID, "period": "2025-Q2", "metric": "revenue", "amount": 50_000_000, "currency": CURRENCY, "budget_version": "v1.0"},
        {"entity_id": ENTITY_ID, "period": "2025-Q2", "metric": "cost", "amount": 38_000_000, "currency": CURRENCY, "budget_version": "v1.0"},
        {"entity_id": ENTITY_ID, "period": "2025-Q3", "metric": "revenue", "amount": 54_000_000, "currency": CURRENCY, "budget_version": "v1.0"},
        {"entity_id": ENTITY_ID, "period": "2025-Q3", "metric": "cost", "amount": 40_000_000, "currency": CURRENCY, "budget_version": "v1.0"},
        {"entity_id": ENTITY_ID, "period": "2025-Q4", "metric": "revenue", "amount": 58_000_000, "currency": CURRENCY, "budget_version": "v1.0"},
        {"entity_id": ENTITY_ID, "period": "2025-Q4", "metric": "cost", "amount": 42_000_000, "currency": CURRENCY, "budget_version": "v1.0"},
    ]
    insert_budget(budgets, db_path)

    # 3. Machine Learning Predictive Forecasts (EAC / ETC)
    now_iso = datetime.now(timezone.utc).isoformat()
    forecasts = [
        # Revenue Forecast
        {
            "forecast_id": f"FC-REV-{uuid4().hex[:8]}",
            "entity_id": ENTITY_ID,
            "metric": "revenue",
            "period": "2025-Q3",
            "point_estimate": 51_500_000,
            "lower": 48_200_000,
            "upper": 54_800_000,
            "confidence": 0.90,
            "model_name": "project_cost_forecaster",
            "model_version": "v2026.1",
            "forecast_as_of": now_iso,
            "data_as_of": "2025-07-05T00:00:00Z",
        },
        {
            "forecast_id": f"FC-REV-{uuid4().hex[:8]}",
            "entity_id": ENTITY_ID,
            "metric": "revenue",
            "period": "2025-Q4",
            "point_estimate": 59_000_000,
            "lower": 54_000_000,
            "upper": 64_000_000,
            "confidence": 0.90,
            "model_name": "project_cost_forecaster",
            "model_version": "v2026.1",
            "forecast_as_of": now_iso,
            "data_as_of": "2025-07-05T00:00:00Z",
        },
        # Cost Forecast
        {
            "forecast_id": f"FC-COST-{uuid4().hex[:8]}",
            "entity_id": ENTITY_ID,
            "metric": "cost",
            "period": "2025-Q3",
            "point_estimate": 43_800_000,
            "lower": 41_500_000,
            "upper": 46_200_000,
            "confidence": 0.90,
            "model_name": "project_cost_forecaster",
            "model_version": "v2026.1",
            "forecast_as_of": now_iso,
            "data_as_of": "2025-07-05T00:00:00Z",
        },
        {
            "forecast_id": f"FC-COST-{uuid4().hex[:8]}",
            "entity_id": ENTITY_ID,
            "metric": "cost",
            "period": "2025-Q4",
            "point_estimate": 44_200_000,
            "lower": 41_000_000,
            "upper": 47_500_000,
            "confidence": 0.90,
            "model_name": "project_cost_forecaster",
            "model_version": "v2026.1",
            "forecast_as_of": now_iso,
            "data_as_of": "2025-07-05T00:00:00Z",
        },
    ]
    insert_forecast(forecasts, db_path)

    # 4. Supporting Technical & Financial Documents (RAG evidence)
    documents = [
        {
            "document_id": "DOC-PROPULSION-01",
            "title": "Propulsion System Delivery & Subcontractor Price Adjustment Memo",
            "document_type": "technical_memo",
            "period": "2025-Q2",
            "version": "1.1",
            "source_uri": "sharepoint://projects/vessel-2026/memos/propulsion_q2.pdf",
            "content": """Summary of Subcontractor Overrun in Q2:
The waterjet and turbine integration milestone incurred an unexpected +4.0M NOK cost increase.
Root causes:
1. Extended drydock alignment tolerance requirements demanded 280 additional engineering labor hours.
2. The German subcontractor invoiced indexation surcharges under clause 14.3 due to raw titanium price spikes.
Status: Milestone successfully passed factory acceptance tests on June 28. Future quarters are expected to stabilize.""",
        },
        {
            "document_id": "DOC-MILESTONE-REV-02",
            "title": "Customer Milestone Billing Postponement Notice (Q2)",
            "document_type": "billing_notice",
            "period": "2025-Q2",
            "version": "1.0",
            "source_uri": "sharepoint://projects/vessel-2026/billing/milestone_q2_deferral.pdf",
            "content": """Milestone Certificate Signing Delay:
Revenue recognition of 5.0M NOK was delayed from late Q2 to early Q3.
Customer QA inspector requested re-verification of the composite hull ultrasonic weld tests.
The test was re-certified as compliant on July 2. Revenue will be billed and recognized in 2025-Q3 with zero contract value loss.""",
        },
        {
            "document_id": "POL-FIN-2026-01",
            "title": "Project Controlling Variance and Escalation Policy",
            "document_type": "governance_policy",
            "period": "2026",
            "version": "1.0",
            "source_uri": "internal://policies/POL-FIN-2026-01.yaml",
            "content": """Policy POL-FIN-2026-01:
Variances exceeding 5% in period cost or revenue require formal root-cause investigation.
Cost overruns exceeding 10% on cumulative EAC require Project Board contingency authorization.
Forecast numbers produced by statistical/ML models must be treated as immutable evidence and never altered manually.""",
        },
    ]
    for doc in documents:
        insert_document(doc, db_path)
