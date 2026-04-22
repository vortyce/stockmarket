import logging
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from app.repositories.options_repo import OptionsRepository
from app.repositories.portfolio_repo import PortfolioRepository
from app.repositories.upside12m_repo import Upside12MRepository
from app.repositories.market_repo import MarketRepository
from app.models.options import OptionSuggestion, OptionChainSnapshot, OptionsPolicyConfig
from app.core.greeks import GreeksCalculator

logger = logging.getLogger(__name__)

class OptionsSuggestionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OptionsRepository(db)
        self.portfolio_repo = PortfolioRepository(db)
        self.upside_repo = Upside12MRepository(db)
        self.market_repo = MarketRepository(db)

    def generate_all_suggestions(self):
        """
        Main orchestration:
        1. Get active policy
        2. Process Covered Calls for portfolio holdings
        3. Process Cash-Secured Puts for high-potential tickers
        """
        policy = self.repo.get_active_policy()
        
        # 1. Covered Calls
        self._process_covered_calls(policy)
        
        # 2. Cash-Secured Puts
        self._process_cash_puts(policy)

    def _process_covered_calls(self, policy: OptionsPolicyConfig):
        positions = self.portfolio_repo.get_positions()
        for pos in positions:
            if not pos.allow_covered_call or pos.is_core_position or pos.quantity < 100:
                continue
                
            chain = self.repo.get_latest_chain(pos.ticker)
            if not chain:
                continue
                
            # CC Logic
            suggestions = self._filter_and_score_options(
                ticker=pos.ticker,
                chain=chain,
                policy=policy,
                suggestion_type="COVERED_CALL",
                available_lots=int(pos.quantity // 100)
            )
            
            # Fallback if empty
            if not suggestions:
                suggestions = self._filter_and_score_options(
                    ticker=pos.ticker,
                    chain=chain,
                    policy=policy,
                    suggestion_type="COVERED_CALL",
                    available_lots=int(pos.quantity // 100),
                    relaxed=True
                )
                
            if suggestions:
                suggestions.sort(key=lambda x: x.overlay_score, reverse=True)
                self.repo.save_suggestions([suggestions[0]])

    def _process_cash_puts(self, policy: OptionsPolicyConfig):
        cash = self.portfolio_repo.get_cash()
        available_cash = float(cash.amount) if cash else 0.0
        
        ranking = self.upside_repo.get_latest_ranking()
        top_tickers = [r.company.ticker for r in ranking[:20]]
        
        for ticker in top_tickers:
            chain = self.repo.get_latest_chain(ticker)
            if not chain:
                continue
                
            suggestions = self._filter_and_score_options(
                ticker=ticker,
                chain=chain,
                policy=policy,
                suggestion_type="CASH_PUT",
                available_cash=available_cash
            )
            
            if not suggestions:
                suggestions = self._filter_and_score_options(
                    ticker=ticker,
                    chain=chain,
                    policy=policy,
                    suggestion_type="CASH_PUT",
                    available_cash=available_cash,
                    relaxed=True
                )
                
            if suggestions:
                suggestions.sort(key=lambda x: x.overlay_score, reverse=True)
                self.repo.save_suggestions([suggestions[0]])

    def _filter_and_score_options(
        self, 
        ticker: str, 
        chain: List[OptionChainSnapshot], 
        policy: OptionsPolicyConfig,
        suggestion_type: str,
        available_lots: int = 0,
        available_cash: float = 0.0,
        relaxed: bool = False
    ) -> List[OptionSuggestion]:
        
        suggestions = []
        
        # Relaxed factors
        liq_multiplier = 0.5 if relaxed else 1.0 # 50% less OI req
        spread_multiplier = 1.5 if relaxed else 1.0 # 50% more spread allowed
        delta_buffer = 0.05 if relaxed else 0.0
        
        # Get Stock Data for scoring
        ranking = self.upside_repo.get_latest_ticker_ranking(ticker)
        company_score = ranking.final_score if ranking else 50.0
        
        for opt in chain:
            # 1. Strategy type filter
            if opt.option_type != ("CALL" if suggestion_type == "COVERED_CALL" else "PUT"):
                continue
            
            # 2. DTE Filter (Stay firm on DTE)
            if not (policy.min_dte <= opt.dte <= policy.max_dte):
                continue
            
            # 3. Price Fallback
            pref_price = opt.mid_price
            if pref_price is None and relaxed:
                pref_price = opt.last # Use last if mid is missing in fallback
            
            if not pref_price or pref_price <= 0:
                continue

            # 4. Delta Calculation
            delta = opt.delta
            # FORCE use of REAL spot price from our market database
            current_spot = self.market_repo.get_latest_price_by_ticker(ticker) or opt.underlying_price
            if current_spot:
                current_spot = float(current_spot)
            
            if delta is None and pref_price and current_spot and current_spot > 0:
                iv = GreeksCalculator.calculate_iv(
                    price=pref_price,
                    spot=current_spot,
                    strike=opt.strike,
                    dte=opt.dte,
                    option_type=opt.option_type
                )
                delta = GreeksCalculator.calculate_delta(
                    spot=current_spot,
                    strike=opt.strike,
                    dte=opt.dte,
                    iv=iv,
                    option_type=opt.option_type
                )
            
            if delta is None: 
                continue
                
            # Delta range check (with buffer in relaxed mode)
            abs_delta = abs(delta)
            d_min = policy.covered_call_delta_min if suggestion_type == "COVERED_CALL" else policy.cash_put_delta_min
            d_max = policy.covered_call_delta_max if suggestion_type == "COVERED_CALL" else policy.cash_put_delta_max
            
            if not (d_min - delta_buffer <= abs_delta <= d_max + delta_buffer):
                continue

            # 5. Liquidity check (relaxed)
            if opt.open_interest and opt.open_interest < (policy.min_open_interest * liq_multiplier):
                continue
            
            # 6. Calculate Scoring
            premium_yield = pref_price / opt.underlying_price if opt.underlying_price > 0 else 0
            annualized_yield = (premium_yield * 365 / opt.dte) if opt.dte > 0 else 0
            safety_margin = abs(opt.strike - opt.underlying_price) / opt.underlying_price
            
            final_score = (
                (company_score * 0.3) + 
                (min(annualized_yield * 2, 1) * 20) + 
                (min(safety_margin * 5, 1) * 20) +   
                (30)
            )
            
            contracts = available_lots if suggestion_type == "COVERED_CALL" else int(available_cash // (float(opt.strike) * 100))
            if contracts <= 0:
                continue

            # 3. Create Suggestion
            status = "ACTIVE" if not relaxed else "LOW_CONFIDENCE"
            reason = "FILTROS ESTREITOS" if not relaxed else "BAIXA CONFIANÇA - FILTROS RELAXADOS"

            suggestions.append(OptionSuggestion(
                ticker=ticker,
                option_symbol=opt.option_symbol,
                option_symbol_raw=opt.option_symbol_raw,
                option_display_code=opt.option_display_code,
                suggestion_type=suggestion_type,
                strike=opt.strike,
                expiration_date=opt.expiration_date,
                delta=delta,
                premium=pref_price,
                overlay_score=final_score,
                contracts=contracts,
                status=status,
                reason_summary=reason,
                created_at=datetime.utcnow()
            ))
            
        return suggestions
            
        return suggestions
