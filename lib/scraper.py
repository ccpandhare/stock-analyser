from typing import Dict, List
import requests
import re

import pandas as pd
from bs4 import BeautifulSoup
from lib.utils.classes import Stock
from lib.utils.args import debug
from lib.utils.row_names import profit_loss_row_names
from bs4 import BeautifulSoup, Tag

# Given a ticker, scrapes the web for information and returns a Stock object
# Ticker: pd.DataFrame: Name, Ticker, URL
def scrape(session: requests.Session, ticker: str) -> Stock:
    debug("Scraping %s" % ticker)
    url = "https://www.screener.in/company/%s/consolidated/" % ticker
    page = session.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    name = soup.find('h1').text
    financial_data_raw_df = parse_table(
        soup.select_one('#profit-loss .data-table'),
        profit_loss_row_names)

    stock = Stock(ticker, name, url)
    stock.set_financial_data_raw(financial_data_raw_df)
    return stock

def parse_table(ref: Tag, row_names: Dict[str, str]) -> pd.DataFrame:
    table = pd.read_html(str(ref), parse_dates=True, header=0, index_col=0)[0]
    table.columns = [parse_header(h) for h in table.columns]
    table.index = [parse_index(i) for i in table.index]
    unimportant_rows = find_unimportant_rows(table.index, row_names)
    table.drop(unimportant_rows, inplace=True)
    table.index = [map_name(i, row_names) for i in table.index]
    return table

def parse_header(header: str) -> str:
    year = re.sub(r'[^\d]*', '', header)
    return header if year == "" else year

def parse_index(index: str) -> str:
    return re.sub(r'[^A-z ]', '', index).strip().lower()

def find_unimportant_rows(indices: List[str], row_names: Dict[str, str]) -> List[str]:
    return [name for name in indices if not name in row_names]

def map_name(name: str, map: Dict[str, str]) -> str:
    return map[name]