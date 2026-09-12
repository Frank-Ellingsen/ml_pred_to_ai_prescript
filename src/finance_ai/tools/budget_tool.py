"""Tool to retrieve approved budget allocations from SQLite."""

from typing import Any

from pydantic import BaseModel, Field

from finance_ai.database.repository import get_budget
from finance_ai.tools.base import BaseTool


class BudgetInput(BaseModel):
    """Input parameters for approved budget lookup."""

    entity_id: str = Field(description="Financial entity identifier")
    metric: str = Field(description="Financial metric (e.g. revenue, cost)")
    period: str = Field(description="Financial period (e.g. 2025-Q2)")


class BudgetTool(BaseTool):
    """Retrieve approved budget figures."""

    name: str = "get_budget"
    description: str = """
    Retrieve the approved baseline budget for an entity, metric, and period.
    Never modify or estimate budget figures yourself.
    """
    args_schema: type[BaseModel] = BudgetInput

    def _run(self, entity_id: str, metric: str, period: str, **kwargs: Any) -> dict[str, Any]:
        result = get_budget(entity_id=entity_id, metric=metric, period=period)
        if result is None:
            return {
                "found": False,
                "entity_id": entity_id,
                "metric": metric,
                "period": period,
            }
        return {
            "found": True,
            "entity_id": result["entity_id"],
            "period": result["period"],
            "metric": result["metric"],
            "amount": str(result["amount"]),
            "currency": result["currency"],
            "budget_version": result["budget_version"],
        }
