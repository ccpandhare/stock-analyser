# Fetches tickers of stocks listed on Indian Stock Exchanges
# returns the first `limit` ticker data

import requests
import pandas as pd
import re
from time import sleep
from bs4 import BeautifulSoup
from typing import List

def fetch(session: requests.Session, limit: int) -> List[str]:
    screen_referer_url: str = 'https://www.screener.in/screen/new/'
    screen_payload = {'sort':'market capitalization','source':'','query': 'Current price '}

    company_tickers = []

    page_iter = 1
    row_iter = 0
    row_count = 50
    while(True):
        screen_url: str = 'https://www.screener.in/screen/raw/'
        # Get the webpage after submitting the query to screen page
        screen_page = session.get(screen_url, params = screen_payload, headers=dict(Referer=screen_referer_url))
        #print(screen_page.url) #Prints the URL of the new web page

        screen_page_soup = BeautifulSoup(screen_page.text, 'html.parser')
        screen_table = screen_page_soup.findAll('table')[0] #Extracting the 1st HTML table from the list

        for anchor in screen_table.findAll('a', target="_blank"):
            if (row_iter >= limit):
                break
            company_url = anchor['href']
            company_ticker = company_url.split('/')[2]
            row_iter = row_iter + 1
            company_tickers.append(company_ticker)
            
        page_iter = page_iter + 1
        screen_referer_url = screen_page.url
        if(row_iter%row_count != 0):
            break
        elif(row_iter >= limit):
            break
        else:
            screen_payload['page'] = str(page_iter)
        sleep(1)
    return company_tickers