import requests
import json

base_url = "http://localhost:8000/api/v1/options/suggestions"

try:
    print("--- Covered Call ---")
    r_cc = requests.get(f"{base_url}/covered-calls")
    if r_cc.status_code == 200 and r_cc.json():
        print(json.dumps(r_cc.json()[0], indent=2))
    else:
        print("None")
        
    print("\n--- Cash-Secured Put ---")
    r_csp = requests.get(f"{base_url}/cash-puts")
    if r_csp.status_code == 200 and r_csp.json():
        print(json.dumps(r_csp.json()[0], indent=2))
    else:
        print("None")
except Exception as e:
    print(f"Error: {e}")
