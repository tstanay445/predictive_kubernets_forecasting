
import os
import requests
import pandas as pd
import time

from prophet import Prophet

PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL",
    "http://localhost:9090"
)

QUERY = "rate(nginx_http_requests_total[1m])"

FORECAST_HORIZON = 120  # 3 minutes


def fetch_prometheus_metrics():
    """
    Fetch historical RPS measurements directly from Prometheus.
    """

    end_time = time.time()
    start_time = end_time - 600

    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query_range",
        params={
            "query": QUERY,
            "start": start_time,
            "end": end_time,
            "step": "5s"
        },
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    print("Prometheus status:", result["status"])
    print("Returned series:", len(result["data"]["result"]))

    if result["status"] != "success":
        raise RuntimeError("Prometheus query failed")

    series = result["data"]["result"]

    if not series:
        raise ValueError("No RPS data returned by Prometheus")

    values = series[0]["values"]

    df = pd.DataFrame(
        values,
        columns=["Timestamp", "Requests/s"]
    )

    df["ds"] = pd.to_datetime(
        df["Timestamp"].astype(float),
        unit="s"
    )

    df["y"] = pd.to_numeric(
        df["Requests/s"],
        errors="coerce"
    )

    df = df[["ds", "y"]].dropna()
    df = df.sort_values("ds").reset_index(drop=True)

    if len(df) < 60:
        raise ValueError(
            f"Insufficient historical observations: {len(df)}"
        )

    print(f"Fetched {len(df)} observations from Prometheus")

    return df


def train_and_forecast():
    """
        Fetch Prometheus metrics, train Prophet,
        and forecast the next two minutes.
    """

    # 1. Fetch historical metrics
    df_prophet = fetch_prometheus_metrics()

    # 2. Initialize Prophet
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=False,
        yearly_seasonality=False,
        seasonality_mode="additive"
    )

    # 3. Add five-minute simulated traffic seasonality
    model.add_seasonality(
        name="simulated_diurnal",
        period=5 / 1440,
        fourier_order=5
    )

    # 4. Train model
    model.fit(df_prophet)

    # 5. Generate future timestamps
    future = model.make_future_dataframe(
        periods=FORECAST_HORIZON,
        freq="s"
    )

    # 6. Generate predictions
    forecast = model.predict(future)

    # Keep only future predictions
    future_forecast = forecast.tail(FORECAST_HORIZON)

    print("\n--- Forecast at different time horizons ---")

    for seconds in [30, 60, 120]:
        row = future_forecast.iloc[seconds - 1]
        print(f"{seconds}s ahead: {row['yhat']:.2f} RPS")

    peak_row = future_forecast.loc[future_forecast["yhat"].idxmax()]

    predicted_demand = max(0.0, float(peak_row["yhat"]))

    confidence_lower = max(
        0.0, float(peak_row["yhat_lower"])
    )

    confidence_upper = max(
        0.0, float(peak_row["yhat_upper"])
    )

    return {
        "predicted_demand": predicted_demand,
        "confidence_lower": confidence_lower,
        "confidence_upper": confidence_upper
    }
