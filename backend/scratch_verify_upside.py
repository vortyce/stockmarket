import requests
import json

tickers = ['PETR4', 'BBAS3', 'ABEV3']
base_url = "http://localhost:8000/api/v1/upside12m"

for t in tickers:
    url = f"{base_url}/{t}"
    print(f"\n--- Testing {t} ---")
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error testing {t}: {e}")
