"""Tool to retrieve authoritative predictive ML forecasts and intervals from SQLite."""

from typing import Any

from pydantic import BaseModel, Field

from finance_ai.database.repository import get_latest_forecast
from finance_ai.tools.base import BaseTool


class ForecastInput(BaseModel):
    """Input parameters for predictive forecast lookup."""

    entity_id: str = Field(description="Financial entity identifier")
    metric: str = Field(description="Financial metric such as revenue or cost")


class ForecastTool(BaseTool):
    """Retrieve authoritative predictive ML forecasts with prediction intervals."""

    name: str = "get_forecast"
    description: str = """
    Retrieve the latest authoritative predictive ML forecast.
    The returned forecast is immutable evidence.
    Never modify, recalculate, replace, or estimate forecast values yourself.
    """
    args_schema: type[BaseModel] = ForecastInput

    def _run(self, entity_id: str, metric: str, **kwargs: Any) -> dict[str, Any]:
        result = get_latest_forecast(entity_id=entity_id, metric=metric)
        if result is None:
            return {
                "found": False,
                "entity_id": entity_id,
                "metric": metric,
            }

        return {
            "found": True,
            "entity_id": result["entity_id"],
            "metric": result["metric"],
            "model_name": result["model_name"],
            "model_version": result["model_version"],
            "forecast_as_of": result["forecast_as_of"],
            "data_as_of": result["data_as_of"],
            "forecast": [
                {
                    "period": point["period"],
                    "point_estimate": str(point["point_estimate"]),
                    "lower": str(point["lower"]) if point["lower"] is not None else None,
                    "upper": str(point["upper"]) if point["upper"] is not None else None,
                    "confidence": point["confidence"],
                }
                for point in result["forecast"]
            ],
        }
