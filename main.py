from fastapi import FastAPI
from pydantic import BaseModel
import math

app = FastAPI(title="Predictive Autoscaling ML Service")

# Define the JSON prediction contract
class ForecastResponse(BaseModel):
    target_workload: str
    forecast_horizon_seconds: int
    predicted_demand: float
    confidence_lower: float
    confidence_upper: float
    recommended_replicas: int

@app.get("/api/v1/forecast/{workload_name}", response_model=ForecastResponse)
def get_forecast(workload_name: str):
    """
    In production, this endpoint will trigger data preparation from Prometheus, 
    run the Prophet forecast, and calculate the required capacity.
    """
    
    # Example logic: extracting the peak prediction from your Prophet forecast dataframe
    # peak_row = forecast.iloc[-3600:].loc[forecast['yhat'].idxmax()]
    
    peak_predicted_demand = 40.0  # Mock value from the peak of your blue line
    confidence_lower = 110.2
    confidence_upper = 120.8
    
    # Simple Scaling Policy: 1 Pod per 20 requests/second
    recommended_capacity = math.ceil(peak_predicted_demand / 20)
    
    return {
        "target_workload": workload_name,
        "forecast_horizon_seconds": 3600,
        "predicted_demand": round(peak_predicted_demand, 2),
        "confidence_lower": round(confidence_lower, 2),
        "confidence_upper": round(confidence_upper, 2),
        "recommended_replicas": recommended_capacity
    }