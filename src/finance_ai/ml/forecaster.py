"""Predictive ML model generating point forecasts and prediction intervals."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import joblib
import numpy as np
from sklearn.linear_model import Ridge

from finance_ai.domain.contracts import PredictionContract, UncertaintyInterval


class ProjectCostForecaster:
    """Predictive ML forecaster for project controlling costs and revenues."""

    def __init__(self, model_version: str = "v2026.1"):
        self.model_version = model_version
        self.model = Ridge(alpha=1.0)
        self.residual_std: float = 0.0
        self.is_fitted: bool = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "ProjectCostForecaster":
        """Fit ridge regression and estimate prediction standard error."""
        self.model.fit(X, y)
        preds = self.model.predict(X)
        residuals = y - preds
        # Degrees of freedom correction
        dof = max(len(y) - X.shape[1], 1)
        self.residual_std = float(np.sqrt(np.sum(residuals**2) / dof))
        self.is_fitted = True
        return self

    def predict(
        self,
        X_future: np.ndarray,
        metric: str = "cost",
        confidence: float = 0.90,
    ) -> list[PredictionContract]:
        """Generate prediction contracts with statistical prediction intervals."""
        if not self.is_fitted:
            raise RuntimeError("Forecaster must be fitted before calling predict().")

        point_estimates = self.model.predict(X_future)

        # Normal approximation factor for prediction interval (1.645 for 90%)
        z_score = 1.645 if confidence >= 0.90 else 1.96
        margin = z_score * max(self.residual_std, 100_000.0)

        now = datetime.now(timezone.utc)
        valid_until = now + timedelta(days=90)

        contracts = []
        for val in point_estimates:
            point = Decimal(str(round(float(val), 2)))
            lower = Decimal(str(round(float(val - margin), 2)))
            upper = Decimal(str(round(float(val + margin), 2)))

            contract = PredictionContract(
                prediction_id=f"PRED-{uuid4().hex[:8]}",
                model_name="project_cost_forecaster",
                model_version=self.model_version,
                prediction=point,
                unit_or_class=f"expected_{metric}_nok",
                uncertainty=UncertaintyInterval(
                    type="prediction_interval",
                    lower=lower,
                    upper=upper,
                    confidence=confidence,
                ),
                feature_as_of=now,
                valid_until=valid_until,
                warnings=[],
                schema_version="1.0",
            )
            contracts.append(contract)

        return contracts

    def save(self, filepath: Path | str) -> None:
        """Persist model artifacts to disk."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "residual_std": self.residual_std,
                "version": self.model_version,
                "is_fitted": self.is_fitted,
            },
            filepath,
        )

    @classmethod
    def load(cls, filepath: Path | str) -> "ProjectCostForecaster":
        """Load model artifacts from disk."""
        data = joblib.load(filepath)
        forecaster = cls(model_version=data.get("version", "v2026.1"))
        forecaster.model = data["model"]
        forecaster.residual_std = data["residual_std"]
        forecaster.is_fitted = data["is_fitted"]
        return forecaster
