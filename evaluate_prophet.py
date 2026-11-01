
import pandas as pd
import matplotlib.pyplot as plt

from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Load the Prometheus-collected experiment snapshot
df = pd.read_csv("prometheus_rps_history.csv")

df["Timestamp"] = pd.to_datetime(df["Timestamp"])

df_prophet = pd.DataFrame({
    "ds": df["Timestamp"],
    "y": df["Requests/s"]
})

# Chronological split: first 2 cycles for training
train = df_prophet.iloc[:120].copy()
test = df_prophet.iloc[120:].copy()

# Initialize Prophet
model = Prophet(
    daily_seasonality=False,
    weekly_seasonality=False,
    yearly_seasonality=False,
    seasonality_mode="additive"
)

model.add_seasonality(
    name="simulated_diurnal",
    period=5/1440,
    fourier_order=5
)

# Train
model.fit(train)

# Forecast at the exact timestamps of the third cycle
future = test[["ds"]].copy()
forecast = model.predict(future)

# Compare predictions with actual values
actual = test["y"].to_numpy()
predicted = forecast["yhat"].to_numpy()

mae = mean_absolute_error(actual, predicted)
rmse = np.sqrt(mean_squared_error(actual, predicted))

print("Prophet Evaluation")
print("------------------")
print(f"Training samples: {len(train)}")
print(f"Testing samples: {len(test)}")
print(f"MAE: {mae:.4f} RPS")
print(f"RMSE: {rmse:.4f} RPS")

# Plot actual vs predicted
plt.figure(figsize=(13, 5))

plt.plot(test["ds"], actual, label="Actual RPS")
plt.plot(test["ds"], predicted, label="Predicted RPS")

plt.title("Prophet: Actual vs Predicted RPS")
plt.xlabel("Time")
plt.ylabel("Requests per second")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
