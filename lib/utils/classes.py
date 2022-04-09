import datetime
from typing import List, TypedDict

class Document:
    name: str
    url: str
    date: datetime.date

class ChronologicalFloat(TypedDict):
    title: str
    value: float

class Stock:
    ticker: str
    name: str
    url: str

    net_profit: List[ChronologicalFloat]

    def __init__(self, ticker, name, url, net_profit):
        self.ticker = ticker
        self.name = name
        self.url = url
        self.net_profit = net_profit
    