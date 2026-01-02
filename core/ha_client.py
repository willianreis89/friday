import os
import requests

HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# ---------------- CORE CALL ----------------

def call_service(domain: str, service: str, data: dict):
    url = f"{HA_URL}/api/services/{domain}/{service}"
    r = requests.post(url, headers=HEADERS, json=data, timeout=5)
    r.raise_for_status()
    return True

# ---------------- STATES ----------------

def get_all_states():
    url = f"{HA_URL}/api/states"
    r = requests.get(url, headers=HEADERS, timeout=5)
    r.raise_for_status()
    return r.json()

def get_state(entity_id: str) -> str | None:
    for e in get_all_states():
        if e["entity_id"] == entity_id:
            return e["state"]
    return None
