import requests
import re

from bs4 import BeautifulSoup
from lib.utils.classes import Stock
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
    profit_loss_table = parse_table(soup.select_one('#profit-loss .data-table'))

def parse_table(ref: Tag):
    cols = [th.text for th in ref.select('thead th:not(.text)')]
    debug(cols)

def parse_header(header: str) -> str:
    if header.s
