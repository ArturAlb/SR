import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time

SIGNALING_URL = "https://signaling_server:8443/signal"

# Disable SSL verification for self-signed certs (for local dev only)
VERIFY_SSL = False

def post_signal(peer, data):
    requests.post(f"{SIGNALING_URL}/{peer}", json=data, verify=VERIFY_SSL)

def get_signal(peer):
    resp = requests.get(f"{SIGNALING_URL}/{peer}", verify=VERIFY_SSL)
    if resp.ok:
        return resp.json()
    return None

def wait_for_signal(peer, expected_type=None, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        data = get_signal(peer)
        if data and (expected_type is None or data.get('type') == expected_type):
            return data
        time.sleep(1)
    return None
