from sqlalchemy.orm import Session
from datetime import date
import logging
from app.models.company import Company
from app.models.financials import FinancialsAnnual
from app.models.market import MarketSnapshot
from app.models.sector import SectorConfig
from app.models.score import ScoreSnapshot
from app.services.scoring import ScoringEngine
from app.repositories.score_repo import ScoreRepository

logger = logging.getLogger(__name__)

class ScoringService:
    def __init__(self, db: Session):
        self.db = db
        self.score_repo = ScoreRepository(db)

    def calculate_and_save(self, ticker: str):
        logger.info(f"Calculating score for {ticker}...")
        
        # 1. Fetch all data
        company = self.db.query(Company).filter(Company.ticker == ticker).first()
        if not company:
            logger.error(f"Company {ticker} not found")
            return
            
        sector_cfg = self.db.query(SectorConfig).filter(
            SectorConfig.sector.ilike(f"%{company.sector}%")
        ).first()
        
        if not sector_cfg:
            # Fallback to a default configuration if "OUTROS" or the specific sector is missing
            logger.warning(f"Sector config for {company.sector} not found. Using defaults.")
            from types import SimpleNamespace
            sector_cfg = SimpleNamespace(
                weight_quality=0.25,
                weight_valuation=0.25,
                weight_dividends=0.20,
                weight_trend=0.15,
                weight_gov_liq=0.15,
                use_debt_ebitda=True
            )
            
        financials = self.db.query(FinancialsAnnual).filter(
            FinancialsAnnual.company_id == company.id
        ).order_by(FinancialsAnnual.year.desc()).all()
        
        if not financials:
            logger.warning(f"No financials found for {ticker}")
            return
            
        latest_fin = financials[0]
        prev_fin = financials[1] if len(financials) > 1 else None
        
        market = self.db.query(MarketSnapshot).filter(
            MarketSnapshot.company_id == company.id
        ).order_by(MarketSnapshot.as_of_date.desc()).first()
        
        if not market:
            logger.warning(f"No market snapshot found for {ticker}")
            return

        # 2. Calculate Raw Scores
        q_raw = ScoringEngine.calculate_quality_raw(latest_fin, sector_cfg)
        v_raw = ScoringEngine.calculate_valuation_raw(market, sector_cfg)
        d_raw = ScoringEngine.calculate_dividends_raw(market, latest_fin)
        t_raw = ScoringEngine.calculate_trend_raw(latest_fin, prev_fin)
        g_raw = ScoringEngine.calculate_gov_liq_raw(company)

        # 3. Apply Weights
        q_weight = float(sector_cfg.weight_quality)
        v_weight = float(sector_cfg.weight_valuation)
        d_weight = float(sector_cfg.weight_dividends)
        t_weight = float(sector_cfg.weight_trend)
        g_weight = float(sector_cfg.weight_gov_liq)

        q_weighted = q_raw * q_weight
        v_weighted = v_raw * v_weight
        d_weighted = d_raw * d_weight
        t_weighted = t_raw * t_weight
        g_weighted = g_raw * g_weight

        # 4. Explicit Penalties
        penalty = 0.0
        summary_parts = []
        
        # Penalty: Negative Equity
        if float(latest_fin.equity or 0) <= 0:
            penalty += 50.0
            summary_parts.append("PENALIDADE: Patrimônio Líquido Negativo.")
            
        # Penalty: Extreme Debt (only if sector uses debt)
        if sector_cfg.use_debt_ebitda:
            debt_ebitda = float(latest_fin.net_debt or 0) / float(latest_fin.ebitda or 1)
            if debt_ebitda > 5.0:
                penalty += 20.0
                summary_parts.append("PENALIDADE: Alavancagem Extrema (>5x).")

        base_score = q_weighted + v_weighted + d_weighted + t_weighted + g_weighted
        final_score = max(0.0, base_score - penalty)

        # 5. Bucket & Rating Class
        bucket = self._determine_bucket(q_raw, v_raw, d_raw, final_score)
        rating = self._determine_rating(final_score)

        # 6. Save Snapshot
        snapshot = {
            "company_id": company.id,
            "as_of_date": date.today(),
            "model_version": "v1.0.0",
            "quality_raw": q_raw,
            "valuation_raw": v_raw,
            "dividends_raw": d_raw,
            "trend_raw": t_raw,
            "gov_liq_raw": g_raw,
            "quality_weighted": q_weighted,
            "valuation_weighted": v_weighted,
            "dividends_weighted": d_weighted,
            "trend_weighted": t_weighted,
            "gov_liq_weighted": g_weighted,
            "penalty": penalty,
            "final_score": final_score,
            "rating_class": rating,
            "bucket": bucket,
            "summary": " | ".join(summary_parts) if summary_parts else "Perfil saudável."
        }
        
        self.score_repo.upsert_score_snapshot(snapshot)
        logger.info(f"Score for {ticker} saved: {final_score}")
        return final_score

    def _determine_bucket(self, q, v, d, final):
        # 1. Top Pick: High overall score and Minimum Quality
        if final >= 72 and q >= 65: return "Top Pick"
        
        # 2. Value Trap: Cheap but very bad quality (Priority)
        if v >= 75 and q < 40: return "Value Trap"
        
        # 3. Dividend Yield: High points in Dividends block AND NOT Descartar rating
        # This prevents "falling knives" with high yields from dominating.
        if d >= 75 and final >= 45: return "Dividend Yield"
        
        # 4. Qualidade com Desconto: Good quality but very cheap
        if q >= 60 and v >= 70: return "Qualidade com Desconto"
        
        # 5. Lixo: Very low quality
        if q < 25: return "Lixo"
        
        return "Neutro"

    def _determine_rating(self, score):
        if score >= 70: return "Compra"
        if score >= 45: return "Monitorar"
        return "Descartar"
