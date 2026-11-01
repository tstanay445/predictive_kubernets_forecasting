import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("prometheus_rps_history.csv")

df["Timestamp"] = pd.to_datetime(df["Timestamp"])

plt.figure(figsize=(14, 5))
plt.plot(df["Timestamp"], df["Requests/s"])

plt.title("Actual RPS - Three Simulated Traffic Cycles")
plt.xlabel("Time")
plt.ylabel("Requests per second")
plt.grid(True)
plt.tight_layout()
plt.show()