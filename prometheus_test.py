
import requests

PROMETHEUS_URL = "http://localhost:9090"

query = "rate(nginx_http_requests_total[1m])"

response = requests.get(
    f"{PROMETHEUS_URL}/api/v1/query",
    params={"query": query}
)

response.raise_for_status()

result = response.json()

if result["status"] == "success":
    for metric in result["data"]["result"]:
        rps = float(metric["value"][1])
        print(f"Current RPS: {rps:.4f}")
else:
    print("Prometheus query failed:", result)
