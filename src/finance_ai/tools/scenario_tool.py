"""Tool for running bounded deterministic financial scenarios."""

from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field

from finance_ai.tools.base import BaseTool


class ScenarioAssumption(BaseModel):
    """Assumption for a financial variable adjustment."""

    variable: Literal["revenue", "cost"]
    change_pct: Decimal = Field(
        ge=Decimal("-0.50"),
        le=Decimal("0.50"),
        description="Percentage adjustment between -0.50 (-50%) and +0.50 (+50%)",
    )


class ScenarioInput(BaseModel):
    """Input parameters for scenario modeling."""

    baseline_revenue: Decimal = Field(description="Baseline period revenue")
    baseline_cost: Decimal = Field(description="Baseline period cost")
    assumptions: list[ScenarioAssumption] = Field(description="List of variable adjustments")


class ScenarioTool(BaseTool):
    """Run bounded deterministic financial scenario simulations."""

    name: str = "run_financial_scenario"
    description: str = """
    Run a bounded deterministic financial scenario.
    Supported variables are revenue and cost.
    Percentage changes must remain between -50% and +50%.
    Use this tool instead of calculating scenario financial values yourself.
    """
    args_schema: type[BaseModel] = ScenarioInput

    def _run(
        self,
        baseline_revenue: Decimal,
        baseline_cost: Decimal,
        assumptions: list[dict[str, Any] | ScenarioAssumption],
        **kwargs: Any,
    ) -> dict[str, Any]:
        revenue = baseline_revenue
        cost = baseline_cost

        validated = [
            a if isinstance(a, ScenarioAssumption) else ScenarioAssumption.model_validate(a)
            for a in assumptions
        ]

        for assumption in validated:
            if assumption.variable == "revenue":
                revenue *= Decimal("1") + assumption.change_pct
            elif assumption.variable == "cost":
                cost *= Decimal("1") + assumption.change_pct

        baseline_margin = baseline_revenue - baseline_cost
        scenario_margin = revenue - cost
        margin_change = scenario_margin - baseline_margin

        return {
            "baseline": {
                "revenue": str(baseline_revenue),
                "cost": str(baseline_cost),
                "margin": str(baseline_margin),
            },
            "scenario": {
                "revenue": str(round(revenue, 2)),
                "cost": str(round(cost, 2)),
                "margin": str(round(scenario_margin, 2)),
            },
            "margin_change": str(round(margin_change, 2)),
            "assumptions": [a.model_dump(mode="json") for a in validated],
        }
