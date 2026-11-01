
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("prometheus_rps_history.csv")

df["Timestamp"] = pd.to_datetime(df["Timestamp"])

plt.figure(figsize=(12, 5))
plt.plot(df["Timestamp"], df["Requests/s"])

plt.title("Requests Per Second - Prometheus")
plt.xlabel("Time")
plt.ylabel("Requests / Second")
plt.grid(True)

plt.tight_layout()
plt.show()
