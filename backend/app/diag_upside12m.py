from app.db.session import SessionLocal
from app.models.upside12m import Upside12MSnapshot, Upside12MRanking, ResearchTarget
from app.models.company import Company
from app.models.market import MarketSnapshot
from sqlalchemy import select

db = SessionLocal()

# 1. Full ranking table with all blocks
print("=" * 120)
print(f"{'#':>3} {'Ticker':<8} {'Upside':>7} {'Rerating':>9} {'RecupOp':>8} {'Assim':>6} {'GovLiq':>7} {'Penalty':>8} {'Score':>6} {'Bucket':<30} {'Rating'}")
print("=" * 120)

results = db.query(Upside12MSnapshot, Company).join(
    Company, Upside12MSnapshot.company_id == Company.id
).order_by(Upside12MSnapshot.final_score.desc()).all()

for i, (s, c) in enumerate(results, 1):
    print(f"{i:>3} {c.ticker:<8} {s.upside_ext_raw:>7.1f} {s.rerating_raw:>9.1f} {s.recup_operacional_raw:>8.1f} {s.assimetria_raw:>6.1f} {s.gov_liq_raw:>7.1f} {s.penalties_raw:>8.1f} {s.final_score:>6.2f} {s.bucket:<30} {s.rating_class}")

print()
print("=" * 120)
print("RESEARCH TARGETS SEED")
print("=" * 120)
print(f"{'Ticker':<8} {'Price Now':>10} {'Target Price':>13} {'Upside %':>9} {'Source':<15}")
print("-" * 70)

targets = db.query(ResearchTarget, Company).join(Company, ResearchTarget.company_id == Company.id).all()
for t, c in sorted(targets, key=lambda x: x[1].ticker):
    upside_pct = ((t.target_price / t.current_price_snapshot) - 1) * 100 if t.current_price_snapshot else 0
    print(f"{c.ticker:<8} {t.current_price_snapshot:>10.2f} {t.target_price:>13.2f} {upside_pct:>9.1f}% {t.source_name:<15}")

db.close()
