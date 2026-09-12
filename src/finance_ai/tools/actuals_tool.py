"""Tool to retrieve validated historical financial actuals from SQLite."""

from typing import Any

from pydantic import BaseModel, Field

from finance_ai.database.repository import get_actuals
from finance_ai.tools.base import BaseTool


class ActualsInput(BaseModel):
    """Input parameters for historical actuals retrieval."""

    entity_id: str = Field(description="Financial entity identifier (e.g. Project-Vessel-2026)")


class FinancialActualsTool(BaseTool):
    """Retrieve validated historical financial actuals."""

    name: str = "get_financial_actuals"
    description: str = """
    Retrieve validated historical financial actuals.
    Use this tool whenever historical revenue, cost, customer, or unit values are required.
    Never estimate or invent historical financial values yourself.
    """
    args_schema: type[BaseModel] = ActualsInput

    def _run(self, entity_id: str, **kwargs: Any) -> list[dict[str, Any]]:
        rows = get_actuals(entity_id=entity_id)
        return [
            {
                "entity_id": row["entity_id"],
                "period": row["period"],
                "revenue": str(row["revenue"]),
                "cost": str(row["cost"]),
                "customers": row["customers"],
                "units": row["units"],
                "currency": row["currency"],
                "data_as_of": row["data_as_of"],
            }
            for row in rows
        ]
