from app.db.session import SessionLocal
from app.models.options import OptionPosition
from datetime import datetime, date, timedelta

def seed_test_position():
    db = SessionLocal()
    try:
        # Create a test position (Covered Call on PETR4)
        # Entry price 1.0, Strike 34.0, Expiring in 20 days (Signal EXIT_TIME)
        pos = OptionPosition(
            asset_ticker="PETR4",
            option_symbol="PETRE340",
            option_type="CALL",
            contracts=10,
            strike=34.0,
            expiration_date=date.today() + timedelta(days=20),
            entry_price=1.0,
            entry_date=date.today(),
            status="OPEN"
        )
        db.add(pos)
        
        # Create another test position (Signal EXIT_PROFIT)
        # Entry price 2.0, Expiring in 40 days
        pos2 = OptionPosition(
            asset_ticker="VALE3",
            option_symbol="VALEE900",
            option_type="CALL",
            contracts=5,
            strike=90.0,
            expiration_date=date.today() + timedelta(days=40),
            entry_price=2.0,
            entry_date=date.today() - timedelta(days=5),
            status="OPEN"
        )
        db.add(pos2)
        
        db.commit()
        print("Test positions seeded successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_position()
