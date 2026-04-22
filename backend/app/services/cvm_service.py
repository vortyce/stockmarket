import os
import requests
import zipfile
import io
import pandas as pd
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.company_repo import CompanyRepository
from app.repositories.financials_repo import FinancialsRepository
from app.services.financial_utils import calculate_financial_ratios

logger = logging.getLogger(__name__)

class CVMService:
    BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/"
    
    # Mapping CVM Accounts to our FinancialsAnnual fields
    # Format: { CD_CONTA: field_name }
    ACCOUNT_MAP = {
        "3.01": "revenue",
        "3.05": "ebit",
        "3.11": "net_income",
        "2.03": "equity",
        "1.01.01": "cash",          # Caixa e Equivalentes
        "2.01.04": "st_debt",       # Empréstimos e Financiamentos (Curto Prazo)
        "2.02.01": "lt_debt",       # Empréstimos e Financiamentos (Longo Prazo)
        "1": "total_assets"
    }

    def __init__(self, db: Session):
        self.db = db
        self.company_repo = CompanyRepository(db)
        self.financial_repo = FinancialsRepository(db)

    def ingest_annual_data(self, years: list[int]):
        """Helper to ingest multiple years and return combined stats."""
        total_processed = 0
        for year in years:
            stats = self.download_and_parse_dfp(year)
            if stats:
                total_processed += stats.get("updated", 0)
        return {"processed": total_processed}

    def download_and_parse_dfp(self, year: int):
        filename = f"dfp_cia_aberta_{year}.zip"
        url = f"{self.BASE_URL}{filename}"
        
        logger.info(f"Downloading CVM DFP for year {year} from {url}")
        
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to download CVM data for {year}: Status {response.status_code}")
            return
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # We need DRE (Income) and BPP (Equity/Liabilities)
            dre_file = f"dfp_cia_aberta_DRE_con_{year}.csv"
            bpp_file = f"dfp_cia_aberta_BPP_con_{year}.csv"
            
            if dre_file not in z.namelist() or bpp_file not in z.namelist():
                logger.error(f"Expected CSV files not found in ZIP for {year}")
                return
            
            # Parse DRE
            with z.open(dre_file) as f:
                df_dre = pd.read_csv(f, sep=";", encoding="ISO-8859-1")
            
            # Parse BPP
            with z.open(bpp_file) as f:
                df_bpp = pd.read_csv(f, sep=";", encoding="ISO-8859-1")
            
            self._process_dataframes(df_dre, df_bpp, year)

    def _process_dataframes(self, df_dre, df_bpp, year):
        # Filter for the latest exercise only (ÚLTIMO) to avoid duplicates from previous years
        df_dre = df_dre[df_dre["ORDEM_EXERC"] == "ÚLTIMO"]
        df_bpp = df_bpp[df_bpp["ORDEM_EXERC"] == "ÚLTIMO"]
        
        # Combine dataframes
        df_combined = pd.concat([df_dre, df_bpp])
        
        # Clean CNPJ in the dataframe to match our DB
        df_combined["CNPJ_CIA_CLEAN"] = df_combined["CNPJ_CIA"].str.replace(r"\D", "", regex=True)
        
        # Filter for accounts we care about
        df_relevant = df_combined[df_combined["CD_CONTA"].isin(self.ACCOUNT_MAP.keys())]
        
        # Group by CNPJ
        grouped = df_relevant.groupby("CNPJ_CIA_CLEAN")
        
        stats = {"inserted": 0, "updated": 0, "errors": 0}
        
        for cnpj, group in grouped:
            from app.models.company import Company
            company = self.db.query(Company).filter(Company.cnpj == cnpj).first()
            if not company:
                continue
            
            financial_data = {
                "company_id": company.id,
                "year": year
            }
            
            for _, row in group.iterrows():
                field = self.ACCOUNT_MAP.get(row["CD_CONTA"])
                if field and field != "total_assets":
                    val = float(row["VL_CONTA"])
                    # Handle Scale (ESCALA_MOEDA)
                    if row["ESCALA_MOEDA"] == "MIL":
                        val *= 1000
                    financial_data[field] = val
            
            try:
                # If we have any data beyond just company_id and year
                if len(financial_data) > 2:
                    # Calculate ratios before saving
                    financial_data = calculate_financial_ratios(financial_data)
                    self.financial_repo.upsert_financials(financial_data)
                    stats["updated"] += 1
            except Exception as e:
                logger.error(f"Error upserting financials for {cnpj}: {e}")
                stats["errors"] += 1
        
        logger.info(f"CVM Ingestion finished for {year}: {stats}")
        return stats
