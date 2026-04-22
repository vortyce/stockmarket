from app.db.session import SessionLocal
from app.models.options import OptionPosition, OptionChainSnapshot
from app.models.company import Company
from app.models.upside12m import Upside12MRanking
from datetime import datetime, date, timedelta
import uuid

def seed_validation_cases():
    db = SessionLocal()
    try:
        # 0. Clean up existing test data to be sure
        db.query(OptionPosition).delete()
        db.query(OptionChainSnapshot).delete()
        db.query(OptionSuggestion).delete()
        db.commit()

        as_of_date = date.today()
        
        # 1. Helper to ensure company and ranking exist
        def setup_company_ranking(ticker, score, rating, bucket):
            co = db.query(Company).filter(Company.ticker == ticker).first()
            if not co:
                co = Company(id=str(uuid.uuid4()), ticker=ticker, name=f"Test {ticker}")
                db.add(co)
                db.commit()
            
            # Upsert ranking
            rk = db.query(Upside12MRanking).filter(Upside12MRanking.company_id == co.id, Upside12MRanking.as_of_date == as_of_date).first()
            if not rk:
                rk = Upside12MRanking(
                    id=str(uuid.uuid4()),
                    company_id=co.id,
                    as_of_date=as_of_date,
                    final_score=score,
                    rating_class=rating,
                    bucket=bucket,
                    position=1
                )
                db.add(rk)
            else:
                rk.final_score = score
                rk.rating_class = rating
                rk.bucket = bucket
            db.commit()
            return co

        # Helper to ensure option snapshot exists (so current_price is not null)
        def setup_snapshot(ticker, symbol, price):
            snap = OptionChainSnapshot(
                ticker=ticker,
                option_symbol=symbol,
                option_type="CALL",
                expiration_date=date.today() + timedelta(days=30),
                dte=30,
                strike=40.0,
                underlying_price=42.0,
                mid_price=price,
                snapshot_date=date.today()
            )
            db.add(snap)
            db.commit()

        # CASE 1: EXIT_TIME + Roll Bloqueado (Score low)
        setup_company_ranking("PETR4", 45.0, "Monitorar", "Neutro")
        setup_snapshot("PETR4", "PETRE100", 0.5)
        pos1 = OptionPosition(
            asset_ticker="PETR4", option_symbol="PETRE100", option_type="CALL",
            contracts=10, strike=34.0, entry_price=1.0, 
            expiration_date=date.today() + timedelta(days=15), # EXIT_TIME
            status="OPEN", entry_date=date.today()
        )
        db.add(pos1)

        # CASE 2: EXIT_PROFIT + Roll Permitido (Score high)
        setup_company_ranking("BBAS3", 75.0, "Compra Forte", "Value")
        setup_snapshot("BBAS3", "BBASD200", 0.9)
        pos2 = OptionPosition(
            asset_ticker="BBAS3", option_symbol="BBASD200", option_type="CALL",
            contracts=10, strike=50.0, entry_price=2.0, # Entry 2, Current 0.9 -> PnL 55%
            expiration_date=date.today() + timedelta(days=40), 
            status="OPEN", entry_date=date.today()
        )
        db.add(pos2)

        # CASE 3: HOLD + Roll Permitido 
        setup_company_ranking("ITUB4", 80.0, "Compra Forte", "Top Pick")
        setup_snapshot("ITUB4", "ITUBE300", 1.8)
        pos3 = OptionPosition(
            asset_ticker="ITUB4", option_symbol="ITUBE300", option_type="CALL",
            contracts=10, strike=30.0, entry_price=2.0, # PnL 10%
            expiration_date=date.today() + timedelta(days=40), 
            status="OPEN", entry_date=date.today()
        )
        db.add(pos3)

        # CASE 4: Roll Bloqueado por Rating (Descartar)
        setup_company_ranking("VALE3", 55.0, "Descartar", "Armadilha de Upside")
        setup_snapshot("VALE3", "VALEE900", 1.0)
        pos4 = OptionPosition(
            asset_ticker="VALE3", option_symbol="VALEE900", option_type="CALL",
            contracts=10, strike=90.0, entry_price=1.0, 
            expiration_date=date.today() + timedelta(days=20), # EXIT_TIME
            status="OPEN", entry_date=date.today()
        )
        db.add(pos4)

        # CASE 5: Roll Bloqueado por Bucket (Penalidade Crítica)
        setup_company_ranking("ABEV3", 65.0, "Compra", "Penalidade Crítica")
        setup_snapshot("ABEV3", "ABEVF150", 0.6)
        pos5 = OptionPosition(
            asset_ticker="ABEV3", option_symbol="ABEVF150", option_type="CALL",
            contracts=10, strike=15.0, entry_price=0.8, 
            expiration_date=date.today() + timedelta(days=22), # HOLD (close to exit)
            status="OPEN", entry_date=date.today()
        )
        db.add(pos5)

        db.commit()
        print("5 Validation cases seeded successfully.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_validation_cases()
