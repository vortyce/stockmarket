import logging

logger = logging.getLogger(__name__)

def calculate_financial_ratios(data: dict) -> dict:
    """
    Calculates ROE, Net Margin, and EBIT Margin from raw figures.
    Modifies the dictionary in place and returns it.
    """
    revenue = float(data.get("revenue") or 0)
    ebit = float(data.get("ebit") or 0)
    ebitda = float(data.get("ebitda") or ebit) # Proxy EBITDA using EBIT for the MVP
    net_income = float(data.get("net_income") or 0)
    equity = float(data.get("equity") or 0)
    
    # Calculate Net Debt
    st_debt = float(data.pop("st_debt", 0))
    lt_debt = float(data.pop("lt_debt", 0))
    cash = float(data.pop("cash", 0))
    
    # Also pop total_assets since it's not in the DB model yet
    data.pop("total_assets", None)
    
    data["net_debt"] = (st_debt + lt_debt) - cash
    data["ebitda"] = ebitda
    
    # 1. ROE (Return on Equity)
    if equity > 0:
        data["roe"] = net_income / equity
    else:
        data["roe"] = 0.0
        
    # 2. Net Margin
    if revenue > 0:
        data["net_margin"] = net_income / revenue
    else:
        data["net_margin"] = 0.0
        
    # 3. EBIT Margin
    if revenue > 0:
        data["ebit_margin"] = ebit / revenue
    else:
        data["ebit_margin"] = 0.0
        
    return data
