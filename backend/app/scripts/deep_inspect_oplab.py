import os, json, requests

def deep_inspect_oplab(ticker):
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
    
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("options", [])
    else:
        items = [data]
        
    if not items:
        print("No options found.")
        return

    # Pick one item and show ALL fields
    print("\n--- Deep Item Inspection ---")
    first_item = items[0]
    print(json.dumps(first_item, indent=2))
    
    print("\n--- Field Summary ---")
    print(", ".join(first_item.keys()))

if __name__ == "__main__":
    # Use PETR4 as it's the most common one to have many options
    deep_inspect_oplab("PETR4")
