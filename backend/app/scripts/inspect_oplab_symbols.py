import os, json, requests

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
    
    # Extract samples
    if isinstance(data, list):
        samples = data[:5]
    elif isinstance(data, dict):
        samples = data.get("options", [])[:5]
    else:
        samples = [data]
        
    print(f"\n--- Raw Sample ---")
    for i, item in enumerate(samples):
        print(f"\nItem {i}:")
        # Keep only symbol related fields
        symbol_fields = {k: v for k, v in item.items() if any(x in k.lower() for x in ["symbol", "name", "code", "label", "ticker"])}
        print(json.dumps(symbol_fields, indent=2))
        
    # Check for underlying fields as well
    if isinstance(data, dict):
        underlying = {k: v for k, v in data.items() if k != "options"}
        print(f"\n--- Underlying Data ---")
        print(json.dumps(underlying, indent=2))

if __name__ == "__main__":
    inspect_oplab("PETR4")
