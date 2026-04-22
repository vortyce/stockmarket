import logging
import sys
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.db.session import SessionLocal

# Import all models to ensure SQLAlchemy registry is populated
import app.models.company
import app.models.market
import app.models.upside12m
import app.models.portfolio
import app.models.options
import app.models.job_log

from app.repositories.options_repo import OptionsRepository
from app.repositories.portfolio_repo import PortfolioRepository
from app.services.options_suggestion_service import OptionsSuggestionService

logging.basicConfig(level=logging.ERROR) # Quiet logs

def run_cc_audit_detailed():
    db = SessionLocal()
    repo = OptionsRepository(db)
    portfolio_repo = PortfolioRepository(db)
    service = OptionsSuggestionService(db)
    
    policy = repo.get_active_policy()
    positions = portfolio_repo.get_positions()
    
    print("\n" + "="*160)
    print(f"{'Ticker':<8} | {'Qty':<8} | {'AllowCC':<7} | {'EligLot':<7} | {'Chain':<6} | {'Cands':<5} | {'Winner Score':<12} | {'Winner Sym':<12} | {'Block Reason'}")
    print("-" * 160)
    
    for pos in positions:
        ticker = pos.ticker
        qty = float(pos.quantity)
        allow = pos.allow_covered_call
        
        eligible_lot = int(qty // 100)
        
        chain = repo.get_latest_chain(ticker)
        ingested = len(chain)
        
        # Actual engine result
        sugs = []
        if allow and eligible_lot > 0 and ingested > 0:
            sugs = service._filter_and_score_options(
                ticker=ticker,
                chain=chain,
                policy=policy,
                suggestion_type="COVERED_CALL",
                available_lots=eligible_lot
            )
        
        candidates_count = len(sugs)
        winner_score = "---"
        winner_sym = "---"
        block_reason = "OK"
        
        if not allow: block_reason = "AllowCC=False"
        elif eligible_lot <= 0: block_reason = "No Lots (<100)"
        elif ingested == 0: block_reason = "No Data"
        elif candidates_count == 0: block_reason = "Filtered/No Cands"
        
        if candidates_count > 0:
            # Sort by score to find winner (mimicking service)
            sugs.sort(key=lambda x: x.overlay_score, reverse=True)
            winner = sugs[0]
            winner_score = f"{winner.overlay_score:.2f}"
            winner_sym = winner.option_symbol
            block_reason = "✅ Selected"

        print(f"{ticker:<8} | {qty:<8.0f} | {str(allow):<7} | {eligible_lot:<7} | {ingested:<6} | {candidates_count:<5} | {winner_score:<12} | {winner_sym:<12} | {block_reason}")

    print("="*160)
    db.close()

if __name__ == "__main__":
    run_cc_audit_detailed()
