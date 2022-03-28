import datetime
import argparse
import requests
import pandas as pd
from os import path
from bs4 import BeautifulSoup
import re
from time import sleep

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

    annual_reports: [Document] = []
    concalls: [Document] = []
    credit_reports: [Document] = []

    def __init__(ticker: str):
        self.ticker = ticker

    def DCF_MC_analysis():
        



class Session:
    """
    Usage: 
    LS = Session('user', 'pass')
    session = LS.mySession()
    ....
    LS.close() or session.close()
    """
    __username: str
    __password: str

    __login_url: str = 'https://www.screener.in/login/'

    __session: [requests.sessions.Session]

    def __init__(self, username: str, password: str):
        #TODO: Remove un necessary stuff. See if we need to store theusername and password in class variables
        self.__username = username
        self.__password = password
        self.__login()

    def __login(self):
        self.__session = requests.Session()
        self.__session.get(self.__login_url)
        csrftoken = self.__session.cookies['csrftoken']

        #Appending the csrftoken to the data payload
        login_payload = {'username':self.__username, 'password':self.__password, 'csrfmiddlewaretoken':csrftoken}
        resp = self.__session.post(self.__login_url, data = login_payload, headers=dict(Referer=self.__login_url))
        
    def mySession(self) -> [requests.sessions.Session]:
        return self.__session

    def closeSession(self):
        self.__session.close()



class CompanyTickers:
    """
    Usage:
    Companies = Companies(session=session,limit=101)
    myCompanies = Companies.getCompanyTickers()
    """
    __screen_url: str = 'https://www.screener.in/screen/raw/'
    __screen_referer_url: str = 'https://www.screener.in/screen/new/'
    __company_search_url = 'https://www.screener.in/api/company/search/'

    __limit: int

    __session: [requests.sessions.Session]

    def __init__(self,session,limit=100000):
        self.__limit = limit
        self.__session = session
        
    def setLimit(self,limit=100000, forceRefetch = False):
        self.__limit = limit
        if(forceRefetch == True):
            self.__fetchCompanies()

    def __fetchCompanies(self):
        screen_referer_url = self.__screen_referer_url
        screen_payload = {'sort':'','source':'','query': 'Current price '}

        companyTickers = pd.DataFrame(columns = ['Name', 'Ticker', 'URL']) #empty DF to append to

        page_iter = 1
        row_iter = 0
        row_count = 50
        while(True):
            # Get the webpage after submitting the query to screen page
            screen_page = self.__session.get(self.__screen_url, params = screen_payload, headers=dict(Referer=screen_referer_url))
            #print(screen_page.url) #Prints the URL of the new web page

            screen_page_soup = BeautifulSoup(screen_page.text, 'html.parser')
            screen_table = screen_page_soup.findAll('table')[0] #Extracting the 1st HTML table from the list

            for anchor in screen_table.findAll('a', target="_blank"):
                company_name = re.findall("\w.+", anchor.text)[0]
                company_url = anchor['href']
                company_ticker = company_url.split('/')[2]
                row_iter = row_iter + 1
                companyTickers.loc[row_iter] = [company_name, company_ticker, company_url]
                
            page_iter = page_iter + 1
            screen_referer_url = screen_page.url
            if(row_iter%row_count != 0):
                break
            elif(row_iter >= self.__limit):
                #companyTickers.set_index('No.', inplace=True)
                companyTickers = companyTickers.loc[companyTickers.index <= (self.__limit)]
                break
            else:
                screen_payload['page'] = str(page_iter)
            sleep(1)
        companyTickers.to_csv('../../CompanyTickers.csv')
        self.__companyTickers = companyTickers

    def getCompanyTickers(self,forceRefetch = False) -> [pd.DataFrame]:
        if((forceRefetch == True) or (path.exists('../../CompanyTickers.csv') == False)):
            self.__fetchCompanies()
        companyTickers = pd.read_csv('../../CompanyTickers.csv', index_col = 0)
        if(companyTickers.shape[0] != self.__limit):
            self.__fetchCompanies()
            companyTickers = pd.read_csv('../../CompanyTickers.csv', index_col = 0)
        return companyTickers