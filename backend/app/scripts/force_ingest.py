import os, logging
from app.db.session import SessionLocal
from app.services.options_chain_service import OptionsChainService
from app.db import base # noqa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manual_ingest")

def run():
    db = SessionLocal()
    svc = OptionsChainService(db)
    tickers = ["PETR4", "VALE3"]
    for t in tickers:
        print(f"Force updating {t}...")
        try:
            count = svc.update_ticker_chain(t)
            print(f"Result for {t}: {count} snapshots saved.")
        except Exception as e:
            print(f"Error for {t}: {e}")
    db.close()

if __name__ == "__main__":
    run()
