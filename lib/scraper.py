from typing import List
import requests
import re

from bs4 import BeautifulSoup
from lib.utils.classes import ChronologicalFloat, Stock
from lib.utils.args import debug
from bs4 import BeautifulSoup, Tag

# Given a ticker, scrapes the web for information and returns a Stock object
# Ticker: pd.DataFrame: Name, Ticker, URL
def scrape(session: requests.Session, ticker: str) -> Stock:
    debug("Scraping %s" % ticker)
    url = "https://www.screener.in/company/%s/consolidated/" % ticker
    page = session.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    name = soup.find('h1').text
    [net_profit] = parse_table(soup.select_one('#profit-loss .data-table'), ['net profit'])

    stock = Stock(ticker, name, url, net_profit)
    return stock

def parse_table(ref: Tag, row_names: List[str]) -> List[List[ChronologicalFloat]]:
    headers = [parse_header(th.text) for th in ref.select('thead th:not(.text)')]
    trs = [ref.find(string=re.compile(row_name, flags=re.I)).parent.parent for row_name in row_names]
    trs_data = [parse_tr(tr, headers) for tr in trs]
    return trs_data

def parse_tr(tr: Tag, headers: List[str]) -> List[ChronologicalFloat]:
    tds = tr.select('td:not(.text)')
    row_data = [{'title': headers[i], 'value': parse_float(tds[i].text)} for i in range(len(tds))]
    return row_data

def parse_header(header: str) -> str:
    year = re.sub(r'[^\d]*', '', header)
    return header if year == "" else year


def parse_float(text: str) -> float:
    return float(re.sub(r',', '', text))