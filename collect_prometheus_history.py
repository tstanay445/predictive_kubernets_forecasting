
import requests
import pandas as pd
import time

PROMETHEUS_URL = "http://localhost:9090"
QUERY = "rate(nginx_http_requests_total[30s])"

data = []

print("Collecting Prometheus RPS for 15 minutes...")

try:
    for i in range(180):
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": QUERY},
            timeout=10
        )
        response.raise_for_status()

        result = response.json()["data"]["result"]

        if result:
            timestamp, rps = result[0]["value"]

            data.append({
                "Timestamp": float(timestamp),
                "Requests/s": float(rps)
            })

            print(f"Sample {i+1}/180 | RPS: {float(rps):.2f}")

        time.sleep(5)

finally:
    if data:
        df = pd.DataFrame(data)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s")
        df.to_csv("prometheus_rps_history.csv", index=False)
        print(f"Saved {len(df)} samples.")
