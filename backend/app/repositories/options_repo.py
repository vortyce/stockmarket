from sqlalchemy.orm import Session
from sqlalchemy import select, delete, desc, update
from app.models.options import OptionChainSnapshot, OptionsPolicyConfig, OptionSuggestion, OptionPosition
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OptionsRepository:
    def __init__(self, db: Session):
        self.db = db

    # Option Chains
    def save_option_chain_batch(self, snapshots: List[OptionChainSnapshot]):
        if not snapshots:
            return
            
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        
        # Strategy: One snapshot official per option per day.
        # 1. Deduplicate by (ticker, symbol, date) in memory first
        unique_snapshots = {}
        for s in snapshots:
            s.ticker = s.ticker.strip().upper()
            s.option_symbol = s.option_symbol.strip().upper()
            key = (s.ticker, s.option_symbol, s.snapshot_date)
            unique_snapshots[key] = s
        
        final_list = list(unique_snapshots.values())
        
        try:
            # 2. Batch process with PostgreSQL Upsert
            for i in range(0, len(final_list), 500): # Process in chunks
                chunk = final_list[i : i + 500]
                
                for s in chunk:
                    # Prepare the data dictionary for the snapshot
                    data = {
                        "id": s.id,
                        "ticker": s.ticker,
                        "option_symbol": s.option_symbol,
                        "option_type": s.option_type,
                        "expiration_date": s.expiration_date,
                        "dte": s.dte,
                        "strike": s.strike,
                        "bid": s.bid,
                        "ask": s.ask,
                        "last": s.last,
                        "mid_price": s.mid_price,
                        "volume": s.volume,
                        "open_interest": s.open_interest,
                        "implied_volatility": s.implied_volatility,
                        "delta": s.delta,
                        "theta": s.theta,
                        "gamma": s.gamma,
                        "vega": s.vega,
                        "underlying_price": s.underlying_price,
                        "option_symbol_raw": s.option_symbol_raw,
                        "option_display_code": s.option_display_code,
                        "snapshot_at": s.snapshot_at,
                        "snapshot_date": s.snapshot_date
                    }
                    
                    stmt = pg_insert(OptionChainSnapshot).values(**data)
                    
                    # Update all fields on conflict except the keys
                    update_cols = {k: v for k, v in data.items() if k not in ["ticker", "option_symbol", "snapshot_date"]}
                    
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["ticker", "option_symbol", "snapshot_date"],
                        set_=update_cols
                    )
                    
                    self.db.execute(stmt)
                
                self.db.commit()
                
            logger.info(f"Successfully upserted {len(final_list)} snapshots")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to upsert option chain batch: {e}")
            raise

    def get_latest_chain(self, ticker: str) -> List[OptionChainSnapshot]:
        # Get the latest snapshot date for this ticker
        latest_date_stmt = select(OptionChainSnapshot.snapshot_date).where(
            OptionChainSnapshot.ticker == ticker
        ).order_by(desc(OptionChainSnapshot.snapshot_date)).limit(1)
        
        latest_date = self.db.execute(latest_date_stmt).scalar_one_or_none()
        if not latest_date:
            return []
            
        # Get all options for that specific date
        stmt = select(OptionChainSnapshot).where(
            OptionChainSnapshot.ticker == ticker,
            OptionChainSnapshot.snapshot_date == latest_date
        )
        return self.db.execute(stmt).scalars().all()

    # Policy
    def get_active_policy(self) -> OptionsPolicyConfig:
        stmt = select(OptionsPolicyConfig).where(OptionsPolicyConfig.is_active == True).limit(1)
        policy = self.db.execute(stmt).scalar_one_or_none()
        if not policy:
            # Create default policy if none exists
            policy = OptionsPolicyConfig(
                policy_name="DEFAULT_POLICY",
                is_active=True
            )
            self.db.add(policy)
            self.db.commit()
            self.db.refresh(policy)
        return policy

    def update_policy(self, policy_id: str, updates: dict) -> Optional[OptionsPolicyConfig]:
        policy = self.db.get(OptionsPolicyConfig, policy_id)
        if not policy:
            return None
        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        self.db.commit()
        self.db.refresh(policy)
        return policy

    # Suggestions
    def save_suggestions(self, suggestions: List[OptionSuggestion]):
        # Strategy: Transition 'ACTIVE' suggestions for these tickers/types to 'SUPERSEDED'
        # Crucial fix: Only supersede same type for same ticker!
        for sug in suggestions:
            self.db.execute(
                update(OptionSuggestion).where(
                    OptionSuggestion.ticker == sug.ticker,
                    OptionSuggestion.suggestion_type == sug.suggestion_type,
                    OptionSuggestion.status == "ACTIVE"
                ).values(status="SUPERSEDED")
            )
            self.db.add(sug)
            
        self.db.commit()

    def get_suggestions(self, suggestion_type: Optional[str] = None) -> List[OptionSuggestion]:
        stmt = select(OptionSuggestion).where(OptionSuggestion.status == "ACTIVE")
        if suggestion_type:
            stmt = stmt.where(OptionSuggestion.suggestion_type == suggestion_type)
        stmt = stmt.order_by(desc(OptionSuggestion.overlay_score))
        return self.db.execute(stmt).scalars().all()

    def accept_suggestion(self, suggestion_id: str, custom_shares: Optional[int] = None) -> Optional[OptionPosition]:
        suggestion = self.db.get(OptionSuggestion, suggestion_id)
        if not suggestion or suggestion.status != "ACTIVE":
            return None
            
        opt_type = "CALL" if suggestion.suggestion_type == "COVERED_CALL" else "PUT"
        
        final_contracts = (custom_shares // 100) if custom_shares is not None else suggestion.contracts
        
        position = OptionPosition(
            asset_ticker=suggestion.ticker,
            option_symbol=suggestion.option_symbol,
            option_type=opt_type,
            contracts=final_contracts,
            strike=suggestion.strike,
            expiration_date=suggestion.expiration_date,
            entry_price=suggestion.premium,
            entry_date=datetime.utcnow().date(),
            status="OPEN"
        )
        
        suggestion.status = "ACCEPTED"
        self.db.add(position)
        self.db.commit()
        self.db.refresh(position)
        return position

    def delete_all_positions(self):
        # Used exclusively to wipe out the hardcoded mock entries
        self.db.execute(delete(OptionPosition))
        self.db.commit()

    # Positions
    def get_open_positions(self) -> List[OptionPosition]:
        return self.db.execute(
            select(OptionPosition).where(OptionPosition.status == "OPEN")
        ).scalars().all()
        
    def get_position(self, position_id: str) -> Optional[OptionPosition]:
        return self.db.get(OptionPosition, position_id)

    def close_position(self, position_id: str, close_price: float, status: str = "CLOSED"):
        pos = self.db.get(OptionPosition, position_id)
        if pos:
            pos.status = status
            pos.close_price = close_price
            pos.closed_at = datetime.utcnow()
            pos.result_amount = (pos.entry_price - close_price) * pos.contracts * 100 # Default PnL calculation
            self.db.commit()
            return pos
        return None
