import os
import requests
from dotenv import load_dotenv

def debug_oplab():
    load_dotenv("backend/.env")
    token = os.getenv("OPLAB_API_TOKEN")
    base_url = "https://api.oplab.com.br/v3"
    
    headers = {
        "Access-Token": token,
        "Content-Type": "application/json"
    }
    
    ticker = "PETR4"
    url = f"{base_url}/market/options/{ticker}"
    
    print(f"Fetching {ticker} from OpLab...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                options = data.get("options", [])
                underlying = data.get("underlying_price") or data.get("close")
                print(f"Underlying Price: {underlying}")
                print(f"Total options found: {len(options)}")
                if options:
                    print("First option sample:", options[0])
            else:
                print(f"Total options found (list): {len(data)}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_oplab()
