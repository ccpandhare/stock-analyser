import datetime
import argparse

class Document:
    name: str
    url: str
    date: datetime.date


class Stock:
    ticker: str
    name: str

    pe_ratio: float
    roe: float
    roce: float

    annual_reports: [Document] = []
    concalls: [Document] = []
    credit_reports: [Document] = []

    def __init__(ticker: str):
        self.ticker = ticker
