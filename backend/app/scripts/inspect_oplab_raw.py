import os, json, requests
from app.db.session import SessionLocal

def inspect_oplab(ticker):
    token = os.getenv("OPLAB_API_TOKEN")
    base_url = "https://api.oplab.com.br/v3"
    url = f"{base_url}/market/options/{ticker}"
    headers = {"Access-Token": token}
    
    print(f"Fetching {ticker} from {url}...")
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"Error: {r.status_code} - {r.text}")
        return
        
    data = r.json()
    
    # Extract a few samples
    # We want to see 'symbol', 'name', 'code', etc.
    if isinstance(data, list):
        samples = data[:5]
    elif isinstance(data, dict):
        samples = data.get("options", [])[:5]
    else:
        samples = [data]
        
    print(f"\n--- Raw Sample (first 5 items) ---")
    for i, item in enumerate(samples):
        print(f"\nItem {i}:")
        print(json.dumps(item, indent=2))

if __name__ == "__main__":
    inspect_oplab("PETR4")
