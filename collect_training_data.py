
import time
import requests
import pandas as pd
from datetime import datetime

PROMETHEUS_URL = "http://localhost:9090"
QUERY = "rate(nginx_http_requests_total[1m])"

DURATION = 3600  # 60 minutes
INTERVAL = 5      # Sample every 5 seconds

data = []

print("Starting 60-minute Prometheus data collection...")

start_time = time.time()

while time.time() - start_time < DURATION:
    try:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": QUERY},
            timeout=10
        )
        response.raise_for_status()

        result = response.json()

        if result["status"] == "success" and result["data"]["result"]:
            rps = float(result["data"]["result"][0]["value"][1])

            data.append({
                "Timestamp": datetime.now(),
                "Requests/s": rps
            })

        elapsed = int(time.time() - start_time)
        print(f"Elapsed: {elapsed}s | Samples: {len(data)}")

    except requests.RequestException as error:
        print("Prometheus request failed:", error)

    time.sleep(INTERVAL)

df = pd.DataFrame(data)
df.to_csv("prometheus_rps_training.csv", index=False)

print("\nCollection completed!")
print(f"Total observations: {len(df)}")
print("Saved to prometheus_rps_training.csv")

