import pytest
from app.models.company import Company
from app.models.score import ScoreSnapshot
from app.models.ranking import RankingSnapshot
from datetime import date

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_companies_empty(client):
    # Depending on DB state, might be empty or not
    response = client.get("/api/v1/companies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_company_not_found(client):
    response = client.get("/api/v1/companies/NONEXISTENT")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticker não encontrado"

def test_company_api_flow(client, db):
    # 1. Create a test company
    test_ticker = "TEST3"
    company = Company(
        ticker=test_ticker,
        company_name="Test Company SA",
        sector="TECNOLOGIA",
        is_active=True
    )
    db.add(company)
    db.commit()
    db.refresh(company)

    # 2. Test GET /companies/{ticker}
    response = client.get(f"/api/v1/companies/{test_ticker}")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == test_ticker
    assert data["company_name"] == "Test Company SA"

    # 3. Test GET /scores/{ticker} (404 as no score yet)
    response = client.get(f"/api/v1/scores/{test_ticker}")
    assert response.status_code == 404

    # 4. Create a test score
    score = ScoreSnapshot(
        company_id=company.id,
        as_of_date=date.today(),
        final_score=85.5,
        rating_class="Compra",
        bucket="Qualidade com Desconto",
        summary="Empresa de teste muito boa"
    )
    db.add(score)
    db.commit()

    # 5. Test GET /scores/{ticker} (Success)
    response = client.get(f"/api/v1/scores/{test_ticker}")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == test_ticker
    assert data["final_score"] == 85.5
    assert data["rating_class"] == "Compra"

def test_rankings_top20(client, db,):
    # Ensure at least one ranking exists
    # We use a subquery to find a valid company_id from our seeded sectors or companies
    company = db.query(Company).first()
    if not company:
        company = Company(ticker="RANK3", company_name="Ranking Co", sector="BANCOS")
        db.add(company)
        db.commit()
    
    ranking = RankingSnapshot(
        company_id=company.id,
        as_of_date=date.today(),
        scope="general",
        position=1,
        final_score=90.0,
        bucket="Top Pick",
        rating_class="Compra"
    )
    db.add(ranking)
    db.commit()

    response = client.get("/api/v1/rankings/top20")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["ticker"] == company.ticker
    assert data[0]["final_score"] == 90.0
