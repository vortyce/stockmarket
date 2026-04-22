import os, requests, json
from dotenv import load_dotenv

def inspect_oplab():
    load_dotenv('backend/.env')
    token = os.getenv('OPLAB_API_TOKEN')
    headers = {'Access-Token': token}
    print("Fetching from OpLab...")
    resp = requests.get('https://api.oplab.com.br/v3/market/options/PETR4', headers=headers)
    
    if resp.status_code != 200:
        print(f"Error {resp.status_code}: {resp.text}")
        return

    data = resp.json()
    options = []
    if isinstance(data, dict):
        options = data.get('options', [])
    else:
        options = data
        
    if options:
        print(f"Total options: {len(options)}")
        # Look for anyone with a value for OI or volume
        for opt in options:
            if opt.get('open_interest') or opt.get('oi') or opt.get('volume') or opt.get('v'):
                print("Detailed Sample with activity:")
                print(json.dumps(opt, indent=2))
                return
        
        print("No active options found. Showing first item:")
        print(json.dumps(options[0], indent=2))
    else:
        print("No options found in list.")

if __name__ == "__main__":
    inspect_oplab()
