import os

import requests
from dotenv import load_dotenv

from utils.logger import log_api_call, setup_logger

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

logger = setup_logger(__name__)

HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

# ---------------- CORE CALL ----------------

def call_service(domain: str, service: str, data: dict):
    url = f"{HA_URL}/api/services/{domain}/{service}"
    logger.debug(f"Chamando servico: {domain}.{service} | Data: {data}")
    
    try:
        r = requests.post(url, headers=HEADERS, json=data, timeout=5)
        r.raise_for_status()
        log_api_call(logger, "POST", url, r.status_code)
        return True
    except requests.exceptions.Timeout:
        log_api_call(logger, "POST", url, error="Timeout (5s)")
        raise
    except requests.exceptions.RequestException as e:
        log_api_call(logger, "POST", url, error=str(e))
        raise

# ---------------- STATES ----------------

def get_all_states():
    url = f"{HA_URL}/api/states"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        r.raise_for_status()
        states = r.json()
        log_api_call(logger, "GET", url, r.status_code)
        logger.debug(f"Recuperados {len(states)} estados")
        return states
    except requests.exceptions.RequestException as e:
        log_api_call(logger, "GET", url, error=str(e))
        raise

def get_state(entity_id: str) -> str | None:
    for e in get_all_states():
        if e["entity_id"] == entity_id:
            return e["state"]
    return None
