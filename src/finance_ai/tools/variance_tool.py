"""Tool for deterministic financial variance calculations."""

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from finance_ai.tools.base import BaseTool


class VarianceInput(BaseModel):
    """Input parameters for financial variance calculation."""

    metric: str = Field(description="Metric being analyzed (e.g. revenue, cost)")
    period: str = Field(description="Period being compared (e.g. 2025-Q2)")
    value: Decimal = Field(description="Actual or forecast value")
    baseline: Decimal = Field(description="Budget or baseline value")
    currency: str = Field(default="NOK", description="Currency symbol/code")


class VarianceTool(BaseTool):
    """Calculate authoritative financial variance."""

    name: str = "calculate_variance"
    description: str = """
    Calculate an authoritative financial variance and variance percentage.
    Use this tool instead of calculating financial variances yourself.
    """
    args_schema: type[BaseModel] = VarianceInput

    def _run(
        self,
        metric: str,
        period: str,
        value: Decimal,
        baseline: Decimal,
        currency: str = "NOK",
        **kwargs: Any,
    ) -> dict[str, Any]:
        variance = value - baseline
        variance_pct = (variance / baseline) if baseline != 0 else None

        return {
            "metric": metric,
            "period": period,
            "value": str(value),
            "baseline": str(baseline),
            "variance": str(variance),
            "variance_pct": str(round(variance_pct, 4)) if variance_pct is not None else None,
            "currency": currency,
        }
