"""Feature engineering for time-series project cost and revenue forecasting."""

import pandas as pd


def prepare_project_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Extract trend, lag, and milestone features from historical series."""
    df_sorted = df.sort_values("period").copy()

    # Time step trend
    df_sorted["step"] = range(len(df_sorted))

    # Lags
    df_sorted["lag_1"] = df_sorted["amount"].shift(1).fillna(df_sorted["amount"].iloc[0])
    df_sorted["rolling_mean_2"] = (
        df_sorted["amount"].rolling(window=2, min_periods=1).mean()
    )

    features = df_sorted[["step", "lag_1", "rolling_mean_2"]]
    target = df_sorted["amount"]

    return features, target
