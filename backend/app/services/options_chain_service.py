import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.options_repo import OptionsRepository
from app.providers.oplab import OplabOptionsProvider
from app.providers.yahoo_options import YahooOptionsProvider
from app.models.options import OptionChainSnapshot

logger = logging.getLogger(__name__)

class OptionsChainService:
    def __init__(self, db: Session):
        self.repo = OptionsRepository(db)
        self.primary_provider = OplabOptionsProvider()
        self.fallback_provider = YahooOptionsProvider()

    def update_ticker_chain(self, ticker: str) -> int:
        """
        Fetches and persists the latest option chain for a ticker.
        Returns the number of options saved.
        """
        logger.info(f"Updating option chain for {ticker}")
        
        # 1. Try Primary
        quotes = self.primary_provider.get_option_chain(ticker)
        
        # 2. Try Fallback if primary failed
        if not quotes:
            logger.info(f"Primary provider failed for {ticker}, trying fallback...")
            quotes = self.fallback_provider.get_option_chain(ticker)
            
        if not quotes:
            logger.warning(f"No option quotes found for {ticker} from any provider")
            return 0
            
        import uuid
        from datetime import datetime
        
        # 3. Convert to snapshots
        snapshots = []
        for q in quotes:
            snapshots.append(OptionChainSnapshot(
                id=str(uuid.uuid4()),
                ticker=q.ticker,
                option_symbol=q.option_symbol,
                option_type=q.option_type,
                expiration_date=q.expiration_date,
                dte=q.dte,
                strike=q.strike,
                bid=q.bid,
                ask=q.ask,
                last=q.last,
                mid_price=q.mid_price,
                volume=q.volume,
                open_interest=q.open_interest,
                implied_volatility=q.implied_volatility,
                delta=q.delta,
                theta=q.theta,
                gamma=q.gamma,
                vega=q.vega,
                underlying_price=q.underlying_price,
                option_symbol_raw=q.option_symbol_raw,
                option_display_code=q.option_display_code,
                snapshot_at=q.snapshot_at,
                snapshot_date=q.snapshot_at.date() if q.snapshot_at else datetime.utcnow().date()
            ))
            
        # 4. Save
        self.repo.save_option_chain_batch(snapshots)
        logger.info(f"Saved {len(snapshots)} option snapshots for {ticker}")
        return len(snapshots)

    def get_latest_chain(self, ticker: str):
        return self.repo.get_latest_chain(ticker)
