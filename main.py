
from fastapi import FastAPI
from pydantic import BaseModel
import math

from data_pipeline import train_and_forecast, FORECAST_HORIZON

app = FastAPI(title="Predictive Autoscaling ML Service")


class ForecastResponse(BaseModel):
    target_workload: str
    forecast_horizon_seconds: int
    predicted_demand: float
    confidence_lower: float
    confidence_upper: float
    recommended_replicas: int


@app.get("/api/v1/forecast/{workload_name}", response_model=ForecastResponse)
def get_forecast(workload_name: str):

    forecast = train_and_forecast()

    predicted_demand = forecast["predicted_demand"]
    confidence_lower = forecast["confidence_lower"]
    confidence_upper = forecast["confidence_upper"]

    # Scaling policy: 1 replica per 20 requests/second
    recommended_replicas = max(1, math.ceil(predicted_demand / 20))

    return {
        "target_workload": workload_name,
        "forecast_horizon_seconds": FORECAST_HORIZON,
        "predicted_demand": round(predicted_demand, 2),
        "confidence_lower": round(confidence_lower, 2),
        "confidence_upper": round(confidence_upper, 2),
        "recommended_replicas": recommended_replicas
    }
