import logging
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.company import Company
from app.models.financials import FinancialsAnnual
from app.models.market import MarketSnapshot
from app.models.upside12m import ResearchTarget

logger = logging.getLogger(__name__)

class Upside12MScoringService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_score(self, company: Company, as_of_date: date) -> dict:
        """
        Calculates the Upside 12M score focusing on re-rating, operational recovery, 
        and asymmetry. Uses relative metrics vs history and sectors.
        """
        result = {
            "company_id": company.id,
            "as_of_date": as_of_date,
            "upside_ext_raw": 0.0,
            "rerating_raw": 0.0,
            "recup_operacional_raw": 0.0,
            "assimetria_raw": 0.0,
            "gov_liq_raw": 0.0,
            "penalties_raw": 0.0,
            "final_score": 0.0,
            "bucket": "Neutro",
            "rating_class": "Neutro",
            "summary": "",
            "model_version": "v1.2"  # v1.2: Banking sector debt penalty exemption
        }

        # Sectors where Net Debt/EBITDA is structurally inapplicable as a penalty signal.
        # Banks, insurers and financials carry client deposits as 'liabilities', not leverage.
        BANKING_SECTORS = {
            "Bancos",
            "Seguros",
            "Serviços Financeiros",
            "Emp. Adm. Part. - Seguradoras e Corretoras",
            "Intermediação Financeira",
            "Fundos",
        }
        is_financial_sector = (company.sector or "") in BANKING_SECTORS

        # 1. Fetch Latest Context
        market_now = self.db.query(MarketSnapshot).filter(
            MarketSnapshot.company_id == company.id
        ).order_by(MarketSnapshot.as_of_date.desc()).first()

        fin_hist = self.db.query(FinancialsAnnual).filter(
            FinancialsAnnual.company_id == company.id
        ).order_by(FinancialsAnnual.year.desc()).limit(2).all()
        
        # Latest Research Target
        target = self.db.query(ResearchTarget).filter(
            ResearchTarget.company_id == company.id
        ).order_by(ResearchTarget.created_at.desc()).first()

        fin_last = fin_hist[0] if len(fin_hist) > 0 else None
        fin_prev = fin_hist[1] if len(fin_hist) > 1 else None

        # 2. Upside Externo (30%)
        # Uses price snapshot from research moment for stability
        if target and target.target_price and target.current_price_snapshot > 0:
            upside_pct = (target.target_price / target.current_price_snapshot) - 1
            # Scale: 0% = 0, 50% = 100
            result["upside_ext_raw"] = max(0.0, min(100.0, (upside_pct / 0.50) * 100))
        
        # 3. Re-rating Potencial (25%) - Relative Comparisons
        # Compare current P/L vs historical avg P/L for this asset
        hist_pe_avg = self.db.query(func.avg(MarketSnapshot.pe)).filter(
            MarketSnapshot.company_id == company.id,
            MarketSnapshot.pe > 0
        ).scalar()
        
        hist_pb_avg = self.db.query(func.avg(MarketSnapshot.pb)).filter(
            MarketSnapshot.company_id == company.id,
            MarketSnapshot.pb > 0
        ).scalar()
        
        rerating_score = 40.0 # Base
        if market_now and market_now.pe and hist_pe_avg:
            pe_discount = (float(hist_pe_avg) - float(market_now.pe)) / float(hist_pe_avg)
            # If current PE is 30% below historical avg -> high score
            rerating_score = max(0.0, min(100.0, 50.0 + (pe_discount * 100.0)))
        elif market_now and market_now.pe:
            # Fallback to absolute if no history
            rerating_score = 100.0 if float(market_now.pe) < 10 else (0.0 if float(market_now.pe) > 25 else 50.0)
            
        result["rerating_raw"] = rerating_score

        # 4. Recuperação Operacional (25%) - Trends and Margins
        recup_score = 30.0 # Base
        margin_expansion = False
        ebitda_growth = False
        profit_reversal = False # Prejuízo -> Lucro
        
        if fin_last and fin_prev:
            ebitda_l = float(fin_last.ebitda or 0)
            ebitda_p = float(fin_prev.ebitda or 0)
            ebitda_growth = ebitda_l > ebitda_p and ebitda_l > 0
            
            nm_l = float(fin_last.net_margin or 0)
            nm_p = float(fin_prev.net_margin or 0)
            margin_expansion = nm_l > nm_p
            
            ni_l = float(fin_last.net_income or 0)
            ni_p = float(fin_prev.net_income or 0)
            profit_reversal = ni_p <= 0 and ni_l > 0
            
            pts = 40.0
            if ebitda_growth: pts += 20.0
            if margin_expansion: pts += 20.0
            if profit_reversal: pts += 20.0
            recup_score = min(100.0, pts)
        
        result["recup_operacional_raw"] = recup_score

        # 5. Assimetria (10%) - Objective and Auditable
        # valuation deprimido + margens melhorando + dívida estável/caindo + upside positivo
        assim_score = 20.0
        debt_stable = True
        if fin_last and fin_prev:
            debt_l = float(fin_last.net_debt or 0)
            debt_p = float(fin_prev.net_debt or 0)
            debt_stable = debt_l <= debt_p * 1.05 # Max 5% increase
            
        if rerating_score > 60 and margin_expansion and debt_stable and result["upside_ext_raw"] > 20:
            assim_score = 90.0
        elif rerating_score > 50 and (margin_expansion or debt_stable):
            assim_score = 50.0
            
        result["assimetria_raw"] = assim_score

        # 6. Governança e Liquidez (10%)
        gov_score = 50.0
        if company.listing_segment == "Novo Mercado":
            gov_score += 30.0
        ff = float(company.free_float or 0)
        if ff > 0.25:
            gov_score += 20.0
        result["gov_liq_raw"] = min(100.0, gov_score)

        # 7. Penalties
        penalties = 0.0
        net_debt_ebitda = 0.0

        if fin_last and fin_last.ebitda and float(fin_last.ebitda) > 0:
            net_debt_ebitda = float(fin_last.net_debt or 0) / float(fin_last.ebitda)
            # Exempt banking/financial sectors: their 'debt' is client deposits, not leverage
            if not is_financial_sector and net_debt_ebitda > 4.0:
                penalties += 40.0

        if fin_last and fin_prev:
            ni_l = float(fin_last.net_income or 0)
            ni_p = float(fin_prev.net_income or 0)
            if ni_p > 0 and ni_l < ni_p * 0.5:
                penalties += 30.0  # Profit drop > 50%
            elif ni_l < 0 and ni_p < 0 and ni_l < ni_p:
                penalties += 50.0  # Worsening losses

        result["penalties_raw"] = penalties

        # Calculate Final Score
        s_base = (
            (result["upside_ext_raw"] * 0.30) +
            (result["rerating_raw"] * 0.25) +
            (result["recup_operacional_raw"] * 0.25) +
            (result["assimetria_raw"] * 0.10) +
            (result["gov_liq_raw"] * 0.10)
        )
        s_final = max(0.0, s_base - result["penalties_raw"])
        result["final_score"] = round(s_final, 2)

        # 8. Buckets with Strict Precedence
        bucket = "Neutro"
        rating = "Monitorar"
        summary = "Ativo sem drivers de assimetria ou re-rating claros no momento."

        # High Quality check for some buckets
        quality_is_low = penalties > 30 or net_debt_ebitda > 3.5

        # P1: Armadilha de Upside (CRITICAL)
        if result["upside_ext_raw"] > 50 and (quality_is_low or result["recup_operacional_raw"] < 45):
            bucket = "Armadilha de Upside"
            rating = "Alerta"
            summary = "Potencial teórico alto em research, mas fundamentos operacionais estão em deterioração ou dívida asfixiante."
        
        # P2: Assimetria Atrativa
        elif result["assimetria_raw"] >= 80 and s_final > 60:
            bucket = "Assimetria Atrativa"
            rating = "Compra Forte"
            summary = "Combinação rara de valuation deprimido, margens em expansão e balanço saudável."
            
        # P3: Recuperação Operacional
        elif result["recup_operacional_raw"] >= 75 and s_final > 55:
            bucket = "Recuperação Operacional"
            rating = "Compra"
            summary = "Fase de turno-around ou ganho de eficiência operacional sólida."
            
        # P4: Re-rating Forte
        elif result["rerating_raw"] >= 80 and not quality_is_low and s_final > 50:
            bucket = "Re-rating Forte"
            rating = "Compra"
            summary = "Ação negociada com desconto agressivo em relação à sua própria história."
            
        # P5: Upside de Research
        elif result["upside_ext_raw"] >= 70 and s_final > 45:
            bucket = "Upside de Research"
            rating = "Monitorar"
            summary = "Destaque por desconto antecipado por analistas de mercado (consenso)."

        if s_final < 30 and bucket == "Neutro":
            rating = "Descartar"
            summary = "Pontuação insuficiente no modelo de valorização 12M."

        result["bucket"] = bucket
        result["rating_class"] = rating
        result["summary"] = summary

        return result
