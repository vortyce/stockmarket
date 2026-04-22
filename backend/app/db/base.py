# Import Base from base_class to avoid circular imports
from app.db.base_class import Base

# Import all models here for Alembic detection
from app.models.company import Company
from app.models.sector import SectorConfig
from app.models.financials import FinancialsAnnual
from app.models.market import MarketSnapshot
from app.models.trend import TrendSnapshot
from app.models.risk import RiskFlag
from app.models.score import ScoreSnapshot
from app.models.ranking import RankingSnapshot
from app.models.job_log import JobLog # noqa
from app.models.portfolio import PortfolioPosition, PortfolioCash # noqa
from app.models.upside12m import ResearchTarget, Upside12MSnapshot, Upside12MRanking # noqa
from app.models.options import OptionChainSnapshot, OptionsPolicyConfig, OptionSuggestion, OptionPosition, OptionRollAction # noqa
