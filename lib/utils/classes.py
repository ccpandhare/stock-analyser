import datetime
import pandas as pd

class Document:
    name: str
    url: str
    date: datetime.date

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

    def __init__(self, ticker, name, url):
        self.ticker = ticker
        self.name = name
        self.url = url
    
    def set_financial_data_raw(self, financial_data_raw):
        self.financial_data_raw = financial_data_raw
    
    def set_cashflow_data_raw(self, cashflow_data_raw):
        self.cashflow_data_raw = cashflow_data_raw
    