import logging
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.options_suggestion_service import OptionsSuggestionService
from app.repositories.options_repo import OptionsRepository
from app.repositories.portfolio_repo import PortfolioRepository
from app.repositories.upside12m_repo import Upside12MRepository
from app.core.greeks import GreeksCalculator
from app.db import base # noqa

def run_debug():
    db = SessionLocal()
    try:
        service = OptionsSuggestionService(db)
        repo = OptionsRepository(db)
        port_repo = PortfolioRepository(db)
        up_repo = Upside12MRepository(db)
        
        policy = repo.get_active_policy()
        tickers = ["PETR4", "VALE3", "BBAS3", "ITUB4"]
        
        print(f"Policy: OI >= {policy.min_open_interest}, Bid >= {policy.min_bid}, Spread <= {policy.max_spread_pct}")
        
        for ticker in tickers:
            print(f'\n--- Debugging {ticker} ---')
            chain = repo.get_latest_chain(ticker)
            print(f'Total Snapshots: {len(chain)}')
            
            # --- COVERED CALL ---
            print('\n[COVERED CALL]')
            pos = next((p for p in port_repo.get_positions() if p.ticker == ticker), None)
            if not pos:
                print('X No portfolio position')
            else:
                available_lots = int(pos.quantity // 100)
                calls = [o for o in chain if o.option_type == 'CALL']
                print(f'1. Total Calls: {len(calls)}')
                
                f_dte = [o for o in calls if policy.min_dte <= o.dte <= policy.max_dte]
                print(f'2. Passed DTE: {len(f_dte)}')
                
                f_price = [o for o in f_dte if (o.mid_price or 0) > 0 or (o.last or 0) > 0]
                print(f'3. Passed Price > 0 (Mid or Last): {len(f_price)}')
                
                valid_delta = 0
                valid_liq = 0
                valid_thesis = 0
                
                ranking = up_repo.get_latest_ticker_ranking(ticker)
                
                for o in f_price:
                    # Calculate delta if missing
                    d = o.delta
                    pref_price = o.mid_price or o.last
                    if d is None:
                        iv = GreeksCalculator.calculate_iv(pref_price, o.underlying_price, o.strike, o.dte, o.option_type)
                        d = GreeksCalculator.calculate_delta(o.underlying_price, o.strike, o.dte, iv, o.option_type)
                    
                    if d and policy.covered_call_delta_min <= abs(d) <= policy.covered_call_delta_max:
                        valid_delta += 1
                        if (o.open_interest or 0) >= policy.min_open_interest:
                            valid_liq += 1
                            if ranking and ranking.final_score > 50 and ranking.rating_class != 'Descartar':
                                valid_thesis += 1
                                
                print(f'4. Passed Delta: {valid_delta}')
                print(f'5. Passed Liquidity: {valid_liq}')
                print(f'6. Passed Thesis: {valid_thesis}')

            # --- CASH PUT ---
            print('\n[CASH PUT]')
            cash = port_repo.get_cash()
            puts = [o for o in chain if o.option_type == 'PUT']
            print(f'1. Total Puts: {len(puts)}')
            
            f_dte = [o for o in puts if policy.min_dte <= o.dte <= policy.max_dte]
            print(f'2. Passed DTE: {len(f_dte)}')
            
            f_price = [o for o in f_dte if (o.mid_price or 0) > 0 or (o.last or 0) > 0]
            print(f'3. Passed Price > 0: {len(f_price)}')
            
            valid_delta = 0
            valid_liq = 0
            valid_thesis = 0
            
            ranking = up_repo.get_latest_ticker_ranking(ticker)

            for o in f_price:
                d = o.delta
                pref_price = o.mid_price or o.last
                if d is None:
                    iv = GreeksCalculator.calculate_iv(pref_price, o.underlying_price, o.strike, o.dte, o.option_type)
                    d = GreeksCalculator.calculate_delta(o.underlying_price, o.strike, o.dte, iv, o.option_type)
                
                if d and policy.cash_put_delta_min <= abs(d) <= policy.cash_put_delta_max:
                    valid_delta += 1
                    if (o.open_interest or 0) >= policy.min_open_interest:
                        valid_liq += 1
                        # Check cash
                        if cash.amount >= (o.strike * 100):
                            if ranking and ranking.final_score > 50 and ranking.rating_class != 'Descartar':
                                valid_thesis += 1

            print(f'4. Passed Delta: {valid_delta}')
            print(f'5. Passed Liquidity: {valid_liq}')
            print(f'6. Passed Thesis & Cash: {valid_thesis}')

    finally:
        db.close()

if __name__ == "__main__":
    run_debug()
