from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def score_bands(value: Optional[float], bands: list[tuple[float, int]]) -> int:
    if value is None:
        return 0
    for threshold, points in bands:
        if value >= threshold:
            return points
    return 0

def score_bands_inverse(value: Optional[float], bands: list[tuple[float, int]]) -> int:
    if value is None:
        return 0
    for threshold, points in bands:
        if value <= threshold:
            return points
    return 0

class ScoringEngine:
    """
    Calibrated Band-Based Scoring Engine (Brazilian Market Context).
    """
    
    @staticmethod
    def calculate_quality_raw(financials: Any, sector_cfg: Any) -> float:
        score = 0
        
        # ROE (Max 35 pts) - Calibrated: 15% is excellent in BR
        score += score_bands(float(financials.roe or 0), [(0.20, 35), (0.15, 30), (0.10, 20), (0.05, 10)])
        
        # Net Margin (Max 25 pts)
        score += score_bands(float(financials.net_margin or 0), [(0.20, 25), (0.12, 20), (0.08, 15), (0.04, 5)])
        
        # ROIC (Max 20 pts)
        score += score_bands(float(financials.roic or 0), [(0.15, 20), (0.10, 15), (0.06, 10), (0.03, 5)])
        
        # Debt/EBITDA (Max 20 pts)
        if sector_cfg.use_debt_ebitda:
            # We use a default ebitda check to avoid division by zero
            ebitda = float(financials.ebitda or financials.ebit or 1e-9)
            debt_ebitda = float(financials.net_debt or 0) / ebitda
            score += score_bands_inverse(debt_ebitda, [(1.0, 20), (2.5, 15), (3.5, 10), (4.5, 5)])
        else:
            score += 20 if float(financials.roe or 0) >= 0.12 else 10
            
        return float(min(score, 100))

    @staticmethod
    def calculate_valuation_raw(market: Any, sector_cfg: Any) -> float:
        score = 0
        
        # P/L (Max 40 pts) - Calibrated
        score += score_bands_inverse(float(market.pe or 99), [(8, 40), (12, 30), (18, 20), (25, 10)])
        
        # P/VP (Max 30 pts)
        score += score_bands_inverse(float(market.pb or 99), [(1.0, 30), (1.5, 25), (2.5, 15), (4.0, 5)])
        
        # EV/EBITDA (Max 30 pts)
        score += score_bands_inverse(float(market.ev_ebitda or 99), [(5, 30), (8, 20), (12, 10), (18, 5)])
        
        return float(min(score, 100))

    @staticmethod
    def calculate_dividends_raw(market: Any, financials: Any) -> float:
        score = 0
        
        # DY (Max 70 pts) - Calibrated
        dy = float(market.dividend_yield or 0)
        # Normalize: detect if it's percentage (e.g. 8.37) vs fraction (0.0837)
        if dy > 0.40: # If yield > 40%, it's likely a percentage (or extreme anomaly)
            dy = dy / 100.0
            
        # Granular bands for Brazilian benchmark (benchmark 6%)
        score += score_bands(dy, [
            (0.12, 70), # Exceptional
            (0.09, 60), # High
            (0.06, 45), # Solid (Benchmark)
            (0.04, 25), # Regular
            (0.02, 10)  # Low
        ])
        
        # Payout (Max 30 pts)
        payout = float(financials.payout or 0.5) # Default to 50% if not available for scoring
        if 0.3 <= payout <= 0.9:
            score += 30
        elif 0.1 <= payout < 0.3:
            score += 15
        
        return float(min(score, 100))

    @staticmethod
    def calculate_trend_raw(current_fin: Any, prev_fin: Optional[Any]) -> float:
        if not prev_fin:
            # If no history, we give a neutral 40 pts baseline instead of 0
            return 40.0
            
        score = 0
        # Revenue Growth (Max 50 pts)
        rev_growth = (float(current_fin.revenue or 0) / float(prev_fin.revenue or 1e-9)) - 1
        score += score_bands(rev_growth, [(0.15, 50), (0.08, 40), (0.02, 30), (0.0, 20), (-0.1, 5)])
        
        # Profit Growth (Max 50 pts)
        ni_growth = (float(current_fin.net_income or 0) / float(prev_fin.net_income or 1e-9)) - 1
        score += score_bands(ni_growth, [(0.20, 50), (0.10, 40), (0.0, 25), (-0.15, 5)])
        
        return float(min(score, 100))

    @staticmethod
    def calculate_gov_liq_raw(company: Any) -> float:
        score = 30 # Higher base
        
        if company.listing_segment in ["Novo Mercado", "NM"]:
            score += 40
        elif company.listing_segment in ["Nível 2", "N2"]:
            score += 20
            
        if float(company.free_float or 0) >= 0.20:
            score += 30
            
        return float(min(score, 100))
