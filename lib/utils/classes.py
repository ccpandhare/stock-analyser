import datetime
from typing import List

class Document:
    name: str
    url: str
    date: datetime.date


class Stock:
    ticker: str
    name: str
    url: str

    pe_ratio: float
    roe: float
    roce: float

    annual_reports: List[Document] = []
    concalls: List[Document] = []
    credit_reports: List[Document] = []

    def __init__(self, ticker: str):
        self.ticker = ticker