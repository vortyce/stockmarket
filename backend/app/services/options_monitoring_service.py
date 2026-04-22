import logging
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from app.repositories.options_repo import OptionsRepository
from app.repositories.upside12m_repo import Upside12MRepository
from app.models.options import OptionPosition, OptionSuggestion, OptionChainSnapshot
from app.services.options_suggestion_service import OptionsSuggestionService

logger = logging.getLogger(__name__)

class OptionsMonitoringService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OptionsRepository(db)
        self.upside_repo = Upside12MRepository(db)
        self.suggestion_service = OptionsSuggestionService(db)

    def get_monitored_positions(self) -> List[Dict[str, Any]]:
        positions = self.repo.get_open_positions()
        monitor_data = []
        
        for pos in positions:
            # 1. Get latest market data for the option
            chain = self.repo.get_latest_chain(pos.asset_ticker)
            current_opt = next((o for o in chain if o.option_symbol == pos.option_symbol), None)
            spot_price = chain[0].underlying_price if chain else None
            
            # 2. Get underlying thesis data
            ranking_item = self.upside_repo.get_latest_ticker_ranking(pos.asset_ticker)
            
            # 3. Calculate PnL and DTE
            current_price = current_opt.mid_price if current_opt else None
            pnl_pct = 0.0
            if current_price is not None and pos.entry_price > 0:
                # For sold options (CC/CSP), PnL is (Entry - Current) / Entry
                pnl_pct = (pos.entry_price - current_price) / pos.entry_price
            
            current_dte = (pos.expiration_date - datetime.utcnow().date()).days
            
            # 4. Validate Thesis for Roll
            is_valid, reason = self._validate_thesis_for_roll(ranking_item)
            
            # 5. Determine Signals
            signal = "HOLD"
            should_close = False
            close_reason = None
            
            if current_dte <= 21:
                signal = "EXIT_TIME"
                should_close = True
                close_reason = "Vencimento próximo (<= 21 DTE)"
            elif pnl_pct >= 0.50:
                signal = "EXIT_PROFIT"
                should_close = True
                close_reason = "Meta de lucro atingida (>= 50%)"
            
            monitor_data.append({
                "position_id": pos.id,
                "ticker": pos.asset_ticker,
                "option_symbol": pos.option_symbol,
                "option_type": pos.option_type,
                "strike": pos.strike,
                "expiration_date": pos.expiration_date,
                "entry_price": pos.entry_price,
                "current_price": current_price,
                "spot_price": spot_price,
                "pnl_pct": pnl_pct * 100,
                "current_dte": current_dte,
                "signal": signal,
                "should_close": should_close,
                "close_reason": close_reason,
                "thesis_valid_for_roll": is_valid,
                "roll_block_reason": reason,
                "score": ranking_item.final_score if ranking_item else None,
                "rating": ranking_item.rating_class if ranking_item else "N/A",
                "bucket": ranking_item.bucket if ranking_item else "N/A"
            })
            
        return monitor_data

    def _validate_thesis_for_roll(self, ranking_item) -> (bool, Optional[str]):
        if not ranking_item:
            return False, "Dados de ranking não encontrados"
            
        # 1. Score check
        if ranking_item.final_score <= 50:
            return False, f"Score insuficiente ({ranking_item.final_score:.1f})"
            
        # 2. Rating check
        if ranking_item.rating_class == "Descartar":
            return False, "Rating marcado como Descartar"
            
        # 3. Bucket check (Critical items)
        critical_buckets = ["Armadilha de Upside", "Penalidade Crítica", "Governança Duvidosa"]
        if ranking_item.bucket in critical_buckets:
            return False, f"Bucket problemático: {ranking_item.bucket}"
            
        return True, None

    def get_roll_suggestions(self) -> List[Dict[str, Any]]:
        monitored = self.get_monitored_positions()
        roll_suggestions = []
        
        # Filter for those needing exit but with valid thesis
        to_roll = [m for m in monitored if m["signal"] != "HOLD" and m["thesis_valid_for_roll"]]
        
        for item in to_roll:
            # Reuses suggestion engine logic to find the next best contract
            policy = self.repo.get_active_policy()
            chain = self.repo.get_latest_chain(item["ticker"])
            
            # Identify suggestion type based on original type (assuming we know if it was CC or CSP)
            # For simplicity, we look at option_symbol structure or underlying (if PUT/CALL)
            pos = self.repo.get_position(item["position_id"])
            sug_type = "COVERED_CALL" if pos.option_type == "CALL" else "CASH_PUT"
            
            new_candidates = self.suggestion_service._filter_and_score_options(
                ticker=item["ticker"],
                chain=chain,
                policy=policy,
                suggestion_type=sug_type,
                available_lots=pos.contracts if sug_type == "COVERED_CALL" else 0,
                available_cash=(pos.strike * pos.contracts * 100) if sug_type == "CASH_PUT" else 0.0
            )
            
            if new_candidates:
                best_new = new_candidates[0] # Highest score
                roll_suggestions.append({
                    "original_position_id": item["position_id"],
                    "ticker": item["ticker"],
                    "current_option": item["option_symbol"],
                    "suggested_new_option": best_new.option_symbol,
                    "strike": best_new.strike,
                    "dte": (best_new.expiration_date - datetime.utcnow().date()).days,
                    "estimated_net_credit": best_new.premium, # Plus the profit from closing the old one
                    "reason": f"Rolagem {item['signal']} - Tese válida"
                })
                
        return roll_suggestions
