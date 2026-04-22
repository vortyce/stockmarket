from app.db.session import SessionLocal
from app.models.upside12m import Upside12MSnapshot
from app.models.company import Company
from app.models.financials import FinancialsAnnual
from app.models.market import MarketSnapshot

db = SessionLocal()

for ticker in ['ABEV3', 'WEGE3', 'BBAS3', 'PETR4', 'LREN3']:
    print(f"\n{'='*70}")
    print(f"  {ticker} — Drill Down")
    print(f"{'='*70}")

    comp = db.query(Company).filter(Company.ticker == ticker).first()
    if not comp:
        print("  Not found"); continue

    snap = db.query(Upside12MSnapshot).filter(
        Upside12MSnapshot.company_id == comp.id
    ).order_by(Upside12MSnapshot.as_of_date.desc()).first()

    fin_hist = db.query(FinancialsAnnual).filter(
        FinancialsAnnual.company_id == comp.id
    ).order_by(FinancialsAnnual.year.desc()).limit(2).all()

    mkt = db.query(MarketSnapshot).filter(
        MarketSnapshot.company_id == comp.id
    ).order_by(MarketSnapshot.as_of_date.desc()).first()

    fin_last = fin_hist[0] if len(fin_hist) > 0 else None
    fin_prev = fin_hist[1] if len(fin_hist) > 1 else None

    print(f"  Sector: {comp.sector}  | Listing: {comp.listing_segment} | Free Float: {comp.free_float}")
    print()
    print(f"  [Market Data]")
    if mkt:
        print(f"    Price: R${float(mkt.price):.2f}")
        print(f"    P/L: {float(mkt.pe):.1f}x" if mkt.pe else "    P/L: -")
        print(f"    P/VP: {float(mkt.pb):.2f}x" if mkt.pb else "    P/VP: -")
        print(f"    EV/EBITDA: {float(mkt.ev_ebitda):.1f}x" if mkt.ev_ebitda else "    EV/EBITDA: -")
        print(f"    Div Yield: {float(mkt.dividend_yield)*100:.1f}%" if mkt.dividend_yield else "    Div Yield: -")
    else:
        print("    No market data")

    print()
    print(f"  [Financials YoY]")
    if fin_last and fin_prev:
        def fmt(v):
            return f"R${v/1e9:.1f}B" if v else "-"
        def pct(v):
            return f"{v*100:.1f}%" if v else "-"
        def chg(a, b, label, scale=1e9):
            if a and b:
                delta = (float(a) - float(b)) / abs(float(b)) * 100 if float(b) != 0 else 0
                sign = "▲" if delta > 0 else "▼"
                return f"  {label:<20}: {fmt(float(a))} ({sign}{abs(delta):.1f}%)"
            return f"  {label:<20}: - / -"
        print(chg(fin_last.ebitda, fin_prev.ebitda, "EBITDA"))
        print(chg(fin_last.net_income, fin_prev.net_income, "Lucro Líquido"))
        print(f"  {'Margem Líquida':<20}: {pct(fin_last.net_margin)} (prev: {pct(fin_prev.net_margin)})")
        print(f"  {'Margem EBIT':<20}: {pct(fin_last.ebit_margin)} (prev: {pct(fin_prev.ebit_margin)})")
        print(f"  {'Dívida Liq':<20}: {fmt(float(fin_last.net_debt))}")
        deb_ebitda = float(fin_last.net_debt or 0) / float(fin_last.ebitda or 1)
        print(f"  {'Net Debt/EBITDA':<20}: {deb_ebitda:.1f}x")
    else:
        print("  Insufficient history")
    
    if snap:
        print()
        print(f"  [Upside 12M Score]")
        print(f"    Upside Ext (30%): {snap.upside_ext_raw:.1f}")
        print(f"    Rerating   (25%): {snap.rerating_raw:.1f}")
        print(f"    Recup Op   (25%): {snap.recup_operacional_raw:.1f}")
        print(f"    Assimetria (10%): {snap.assimetria_raw:.1f}")
        print(f"    Gov/Liq    (10%): {snap.gov_liq_raw:.1f}")
        print(f"    Penalties       : -{snap.penalties_raw:.1f}")
        print(f"    ─────────────────────")
        print(f"    FINAL SCORE     : {snap.final_score:.2f}")
        print(f"    BUCKET          : {snap.bucket}")
        print(f"    RATING          : {snap.rating_class}")

db.close()
