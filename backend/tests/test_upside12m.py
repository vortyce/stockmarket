import pytest
import uuid
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.financials import FinancialsAnnual
from app.models.market import MarketSnapshot
from app.models.upside12m import ResearchTarget, Upside12MSnapshot, Upside12MRanking
from app.repositories.upside12m_repo import Upside12MRepository
from app.services.upside12m_scoring import Upside12MScoringService
from app.main import app
from app.db.session import SessionLocal

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

def unique_ticker(prefix="T"):
    return f"{prefix}{uuid.uuid4().hex[:6].upper()}"

def test_upside_repo(db_session: Session):
    repo = Upside12MRepository(db_session)
    ticker = unique_ticker("TR")
    comp = Company(ticker=ticker, company_name="Test Company", cvm_code="T999", cnpj="T11")
    db_session.add(comp)
    db_session.flush()

    # Test Research Targets
    repo.upsert_research_target({
        "company_id": comp.id,
        "target_price": 50.0,
        "source_name": "Test Bank",
        "rating_recommendation": "Buy",
        "current_price_snapshot": 25.0,
        "as_of_date": date(2023, 1, 1)
    })
    db_session.flush()  # Flush so the query can find the record

    target = repo.get_research_target(comp.id)
    assert target is not None
    assert target.target_price == 50.0

    # Test Snapshot upsert
    snap_data = {
        "company_id": comp.id,
        "as_of_date": date.today(),
        "upside_ext_raw": 100.0,
        "rerating_raw": 50.0,
        "recup_operacional_raw": 50.0,
        "assimetria_raw": 0.0,
        "gov_liq_raw": 10.0,
        "penalties_raw": 0.0,
        "final_score": 56.0,
        "bucket": "Upside de Research",
        "rating_class": "Monitorar",
        "summary": "Mock"
    }
    repo.upsert_snapshot(snap_data)
    db_session.flush()
    snap = repo.get_latest_snapshot(comp.id)
    assert snap is not None
    assert snap.final_score == 56.0

def test_upside_scoring_logic(db_session: Session):
    ticker = unique_ticker("TS")
    comp = Company(ticker=ticker, company_name="Test Score", cvm_code="T888", cnpj="T22")
    db_session.add(comp)
    db_session.flush()

    # Financial history: improvement YoY
    fin_22 = FinancialsAnnual(company_id=comp.id, year=2022, ebitda=100.0, ebit_margin=0.1, net_debt=100.0, net_income=10.0)
    fin_23 = FinancialsAnnual(company_id=comp.id, year=2023, ebitda=200.0, ebit_margin=0.2, net_debt=50.0, net_income=20.0)
    db_session.add_all([fin_22, fin_23])

    # A single market snapshot - avg PE == current, so relative discount = 0
    mkt = MarketSnapshot(company_id=comp.id, as_of_date=date.today(), price=10.0, pe=5.0)
    db_session.add(mkt)
    db_session.flush()

    scoring = Upside12MScoringService(db_session)
    res = scoring.calculate_score(comp, date.today())

    # With avg_pe == current_pe, discount = 0, score = 50.0 (relative path)
    assert 40.0 <= res["rerating_raw"] <= 100.0
    # Recovery: base 40 + ebitda_growth 20 + margin_expansion 20 = 80 (no profit_reversal, both profitable)
    assert res["recup_operacional_raw"] >= 60.0
    # Bucket should be assigned
    assert res["bucket"] in ["Assimetria Atrativa", "Recuperação Operacional", "Re-rating Forte", "Neutro", "Armadilha de Upside"]
    # Penalties should be 0 (healthy)
    assert res["penalties_raw"] == 0.0

def test_endpoints():
    resp = client.get("/api/v1/upside12m/top20")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
