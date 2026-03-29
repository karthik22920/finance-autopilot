from typing import List
from pydantic import BaseModel, Field


class FinancialData(BaseModel):
    ticker: str
    company_name: str
    sector: str
    industry: str
    website: str
    business_summary: str
    market_cap: float = Field(ge=0)
    currency: str
    revenue: List[float]
    net_income: List[float]
    prices: List[float]
    growth: float = 0.0
    upside: float = 0.0 