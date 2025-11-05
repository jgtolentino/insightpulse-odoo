import os, requests

base = "http://superset:8088"
u = os.getenv("ADMIN_USERNAME","admin")
p = os.getenv("ADMIN_PASSWORD","admin")

# Login → access token
tok = requests.post(
    f"{base}/api/v1/security/login",
    json={"username": u, "password": p, "provider": "db", "refresh": True}
).json()["access_token"]
H = {"Authorization": f"Bearer {tok}"}

# Find example dashboards
resp = requests.get(f"{base}/api/v1/dashboard?q=(page_size:1000)", headers=H).json()
targets = [d for d in resp["result"] if "World Bank" in d["dashboard_title"] or "Examples" in d["dashboard_title"]]

for d in targets[:1]:  # just the first good seed
    dash_id = d["id"]
    payload = {
        "dashboard_title": "T&E MVP — Examples Seed",
        "published": True,
        "tags": ["MVP", "Examples", "Demo"]
    }
    requests.put(f"{base}/api/v1/dashboard/{dash_id}", headers=H, json=payload)
print("Published: T&E MVP — Examples Seed")
