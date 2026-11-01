
import pandas as pd
import numpy as np
from prophet import Prophet

CSV_FILE = "prometheus_rps_training.csv"

TRAINING_WINDOW = pd.Timedelta(minutes=10)
HORIZONS = [30, 60, 120]
EVALUATION_INTERVAL = 30
MATCH_TOLERANCE = pd.Timedelta(seconds=3)


def load_data():
    df = pd.read_csv(CSV_FILE)

    df["ds"] = pd.to_datetime(df["Timestamp"])
    df["y"] = pd.to_numeric(df["Requests/s"], errors="coerce")

    df = df[["ds", "y"]].dropna()
    df = df.sort_values("ds").drop_duplicates("ds")
    return df.reset_index(drop=True)


def find_actual_value(df, target_time):
    differences = (df["ds"] - target_time).abs()
    index = differences.idxmin()

    if differences[index] > MATCH_TOLERANCE:
        return None

    return float(df.loc[index, "y"])


def evaluate():
    df = load_data()
    results = []

    first_time = df["ds"].iloc[0]
    last_time = df["ds"].iloc[-1]

    origin = first_time + TRAINING_WINDOW

    while origin + pd.Timedelta(seconds=max(HORIZONS)) <= last_time:

        training_data = df[
            (df["ds"] >= origin - TRAINING_WINDOW) &
            (df["ds"] < origin)
        ][["ds", "y"]].copy()

        if len(training_data) < 60:
            origin += pd.Timedelta(seconds=EVALUATION_INTERVAL)
            continue

        # Model 1: Prophet
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=False,
            yearly_seasonality=False,
            seasonality_mode="additive"
        )

        model.add_seasonality(
            name="simulated_diurnal",
            period=5 / 1440,
            fourier_order=5
        )

        model.fit(training_data)

        # Model 2: Persistence baseline
        last_observed_rps = float(training_data["y"].iloc[-1])

        for horizon in HORIZONS:

            target_time = origin + pd.Timedelta(seconds=horizon)

            # Actual future RPS
            actual = find_actual_value(df, target_time)

            if actual is None:
                continue

            # Prophet prediction
            future = pd.DataFrame({"ds": [target_time]})
            forecast = model.predict(future)

            prophet_prediction = max(
                0.0,
                float(forecast["yhat"].iloc[0])
            )

            # Persistence prediction
            persistence_prediction = max(0.0, last_observed_rps)

            results.append({
                "origin": origin,
                "horizon": horizon,
                "actual": actual,
                "prophet_prediction": prophet_prediction,
                "persistence_prediction": persistence_prediction
            })

        origin += pd.Timedelta(seconds=EVALUATION_INTERVAL)

    results_df = pd.DataFrame(results)

    if results_df.empty:
        raise ValueError("No valid evaluation results.")

    print("\n--- Model Comparison ---")

    for horizon in HORIZONS:

        subset = results_df[
            results_df["horizon"] == horizon
        ]

        if subset.empty:
            continue

        actual = subset["actual"]

        for model_name, column in [
            ("Prophet", "prophet_prediction"),
            ("Persistence", "persistence_prediction")
        ]:

            predicted = subset[column]

            mae = np.mean(np.abs(predicted - actual))

            rmse = np.sqrt(
                np.mean((predicted - actual) ** 2)
            )

            print(f"\nHorizon: {horizon} seconds")
            print(f"Model: {model_name}")
            print(f"Evaluations: {len(subset)}")
            print(f"MAE:  {mae:.4f} RPS")
            print(f"RMSE: {rmse:.4f} RPS")

    results_df.to_csv(
        "model_comparison_results.csv",
        index=False
    )

    print("\nResults saved to model_comparison_results.csv")


if __name__ == "__main__":
    evaluate()
