import os, logging
from app.db.session import SessionLocal
from app.services.options_chain_service import OptionsChainService
from app.db import base # noqa

logging.basicConfig(level=logging.INFO)

def run():
    db = SessionLocal()
    svc = OptionsChainService(db)
    tickers = ['BBAS3', 'ITUB4', 'B3SA3', 'ABEV3', 'BBDC4', 'WEGE3', 'RADL3', 'BBSE3']
    for t in tickers:
        try:
            svc.update_ticker_chain(t)
        except Exception as e:
            print(f"Error for {t}: {e}")
    db.close()

if __name__ == "__main__":
    run()
