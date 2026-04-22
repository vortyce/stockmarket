import math
from typing import Optional, Tuple

class GreeksCalculator:
    """
    Implements Black-Scholes model to calculate Delta, Theta, and Implied Volatility.
    Uses pure Python (math.erf) for the normal cumulative distribution function (CDF).
    """

    @staticmethod
    def norm_cdf(x: float) -> float:
        """Approximation of the cumulative distribution function for a standard normal distribution."""
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    @staticmethod
    def calculate_delta(
        spot: float,
        strike: float,
        dte: int,
        iv: float,
        option_type: str,
        risk_free_rate: float = 0.1075  # Default Selic rate
    ) -> float:
        if dte <= 0 or iv <= 0:
            return 0.0
            
        t = dte / 365.0
        sigma = iv
        r = risk_free_rate
        
        # d1 calculation
        try:
            d1 = (math.log(spot / strike) + (r + 0.5 * sigma**2) * t) / (sigma * math.sqrt(t))
        except (ValueError, ZeroDivisionError):
            return 0.0
        
        if option_type.upper() == "CALL":
            return GreeksCalculator.norm_cdf(d1)
        else:
            return GreeksCalculator.norm_cdf(d1) - 1.0

    @staticmethod
    def calculate_iv(
        price: float,
        spot: float,
        strike: float,
        dte: int,
        option_type: str,
        risk_free_rate: float = 0.1075
    ) -> float:
        """
        Estimates Implied Volatility using the bisection method.
        """
        if dte <= 0 or price <= 0:
            return 0.0
            
        target_price = price
        low = 0.01
        high = 5.0
        
        # Bisection method (stable)
        for _ in range(20):
            mid = (low + high) / 2
            est_price = GreeksCalculator._bs_price(spot, strike, dte, mid, option_type, risk_free_rate)
            if est_price < target_price:
                low = mid
            else:
                high = mid
                
        return (low + high) / 2

    @staticmethod
    def _bs_price(spot: float, strike: float, dte: int, iv: float, option_type: str, r: float) -> float:
        t = dte / 365.0
        sigma = iv
        
        try:
            d1 = (math.log(spot / strike) + (r + 0.5 * sigma**2) * t) / (sigma * math.sqrt(t))
            d2 = d1 - sigma * math.sqrt(t)
        except (ValueError, ZeroDivisionError):
            return 0.0
        
        if option_type.upper() == "CALL":
            price = spot * GreeksCalculator.norm_cdf(d1) - strike * math.exp(-r * t) * GreeksCalculator.norm_cdf(d2)
        else:
            price = strike * math.exp(-r * t) * GreeksCalculator.norm_cdf(-d2) - spot * GreeksCalculator.norm_cdf(-d1)
            
        return price
