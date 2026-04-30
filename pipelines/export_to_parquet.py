import pandas as pd
import requests

API = "http://127.0.0.1:8001/incidents"

res = requests.get(API)
data = res.json()["items"]

df = pd.DataFrame(data)
df.to_parquet("incidents.parquet")

print("Exported to incidents.parquet")
