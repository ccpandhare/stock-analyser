from datetime import datetime
from typing import List, TypedDict
import pandas as pd

class Document(TypedDict):
    name: str
    url: str

class Stock:
    ticker: str
    name: str
    url: str

    # Apparently there's no way to type a DataFrame, thanks Python
    # So here goes
    # rows: net_profit
    # columns: years (or TTM)
    financial_data_raw: pd.DataFrame
    cashflow_data_raw: pd.DataFrame
    balance_sheet_data_raw: pd.DataFrame

    annual_reports: List[Document]
    credit_ratings: List[Document]

    financial_ratios: pd.DataFrame

    roce_above_10: bool
    rising_roce: bool
    roce_avg_bps_increase: float

    yoy_margin_increase_count: int
    negative_margin_count: int
    margin_score: int

    controlled_dpr: bool
    idiot_dividend_policy: list
    idiot_dividend_policy_points: int

    def __init__(self, ticker, name, url):
        self.ticker = ticker
        self.name = name
        self.url = url
    
    def set_financial_data_raw(self, financial_data_raw):
        self.financial_data_raw = financial_data_raw
    
    def set_cashflow_data_raw(self, cashflow_data_raw):
        self.cashflow_data_raw = cashflow_data_raw
    
    def set_balance_sheet_data_raw(self, balance_sheet_data_raw):
        self.balance_sheet_data_raw = balance_sheet_data_raw
    
    def set_annual_reports(self, annual_reports: List[Document]):
        self.annual_reports = annual_reports
    
    def set_credit_ratings(self, credit_ratings: List[Document]):
        self.credit_ratings = credit_ratings

    def set_financial_ratios(self, financial_ratios):
        self.financial_ratios = financial_ratios
    