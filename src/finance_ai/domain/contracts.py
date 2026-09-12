"""Strict typed contracts and boundaries for prediction and decision systems."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Base model that forbids unexpected fields and enforces strict validation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )


class UncertaintyInterval(StrictModel):
    """Uncertainty quantification interval around a point estimate."""

    type: Literal["prediction_interval", "confidence_interval"] = "prediction_interval"
    lower: Decimal
    upper: Decimal
    confidence: float = Field(default=0.90, ge=0.50, le=0.99)


class PredictionContract(StrictModel):
    """Immutable prediction contract grounding ML outputs before passing to GenAI.

    Adheres to the architectural specification in Section 3 of ml_ai.md.
    """

    prediction_id: str = Field(default_factory=lambda: str(uuid4()))
    model_name: str
    model_version: str
    prediction: Decimal
    unit_or_class: str
    uncertainty: UncertaintyInterval
    feature_as_of: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: datetime
    warnings: list[str] = Field(default_factory=list)
    schema_version: str = "1.0"


class FeedbackRecord(StrictModel):
    """Immutable feedback record capturing human decisions and outcomes."""

    feedback_id: str = Field(default_factory=lambda: str(uuid4()))
    analysis_id: str
    decision: Literal["approved", "modified", "rejected", "investigate"]
    actual_outcome: str | None = None
    reviewer: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    comments: str | None = None
