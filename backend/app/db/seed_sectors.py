from app.db.session import SessionLocal
from app.models.sector import SectorConfig

def seed_sectors():
    db = SessionLocal()
    
    sectors = [
        {
            "sector": "BANCOS",
            "weight_quality": 0.35, "weight_valuation": 0.25, "weight_dividends": 0.20,
            "weight_trend": 0.10, "weight_gov_liq": 0.10,
            "use_debt_ebitda": False, "use_pb_strong": True, "use_dividend_strong": True,
            "notes": "Foco em ROE e P/VP."
        },
        {
            "sector": "ELÉTRICAS",
            "weight_quality": 0.25, "weight_valuation": 0.15, "weight_dividends": 0.40,
            "weight_trend": 0.10, "weight_gov_liq": 0.10,
            "use_debt_ebitda": True, "use_pb_strong": False, "use_dividend_strong": True,
            "notes": "Foco em previsibilidade e Dividend Yield."
        },
        {
            "sector": "SANEAMENTO",
            "weight_quality": 0.25, "weight_valuation": 0.20, "weight_dividends": 0.25,
            "weight_trend": 0.20, "weight_gov_liq": 0.10,
            "use_debt_ebitda": True, "use_pb_strong": False, "use_dividend_strong": False,
            "notes": "Foco em concessões e marcos regulatórios."
        },
        {
            "sector": "COMMODITIES",
            "weight_quality": 0.20, "weight_valuation": 0.40, "weight_dividends": 0.15,
            "weight_trend": 0.15, "weight_gov_liq": 0.10,
            "use_debt_ebitda": True, "use_pb_strong": False, "use_dividend_strong": False,
            "notes": "Altamente cíclico, foco em valuation (P/L baixo pode ser armadilha)."
        },
        {
            "sector": "VAREJO",
            "weight_quality": 0.25, "weight_valuation": 0.20, "weight_dividends": 0.05,
            "weight_trend": 0.40, "weight_gov_liq": 0.10,
            "use_debt_ebitda": True, "use_pb_strong": False, "use_dividend_strong": False,
            "notes": "Foco em crescimento de receita e margens YoY."
        }
    ]
    
    try:
        for sector_data in sectors:
            existing = db.query(SectorConfig).filter(SectorConfig.sector == sector_data["sector"]).first()
            if not existing:
                sector = SectorConfig(**sector_data)
                db.add(sector)
        
        db.commit()
        print("Sectores seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding sectors: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sectors()
