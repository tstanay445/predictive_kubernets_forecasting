
import requests
import pandas as pd
import time
from datetime import datetime

PROMETHEUS_URL = "http://localhost:9090"
QUERY = "rate(nginx_http_requests_total[1m])"

data = []

print("Starting RPS collection... Press Ctrl+C to stop.")

try:
    while True:
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": QUERY},
            timeout=10
        )

        response.raise_for_status()
        result = response.json()

        if result["status"] == "success":
            metrics = result["data"]["result"]

            if metrics:
                rps = float(metrics[0]["value"][1])

                timestamp = datetime.now()

                data.append({
                    "Timestamp": timestamp,
                    "Requests/s": rps
                })

                print(f"{timestamp} | RPS: {rps:.4f}")

        time.sleep(5)

except KeyboardInterrupt:
    print("\nStopping collection...")

finally:
    if data:
        df = pd.DataFrame(data)
        df.to_csv("prometheus_rps_history.csv", index=False)
        print(f"Saved {len(df)} samples to prometheus_rps_history.csv")
    else:
        print("No data collected.")
