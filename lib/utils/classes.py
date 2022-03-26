import datetime
import argparse
import requests
import pandas as pd

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

class myLoginSession:
    """
    Usage: 
    LS = myLoginSession('user', 'pass')
    session = LS.mySession()

    """
    __username: str
    __password: str

    __login_url: str = 'https://www.screener.in/login/'

    __session: [requests.sessions.Session]

    def __init__(self, username, password):
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
        
    def mySession(self):
        return self.__session

    def closeSession(self):
        self.__session.close()

class Companies:
    """
    Usage:
    Companies = Companies(session, 101)
    print(Companies.getCompanies()
    """
    __screen_url: str = 'https://www.screener.in/screen/raw/'
    __screen_referer_url: str = 'https://www.screener.in/screen/new/'

    __limit: int
    __companies: [pd.DataFrame]

    __session: [requests.sessions.Session]

    def __init__(self,session,limit=100000):
        self.__limit = limit
        self.__session = session
        self.__companies = pd.DataFrame() #empty DF to append to
        
    def setLimit(self,limit=100000, refetch = False):
        self.__limit = limit
        if(refetch == True):
            self.__fetchCompanies()

    def __fetchCompanies(self):
        screen_referer_url = self.__screen_referer_url
        screen_payload = {'sort':'','source':'','query': 'Current price '}

        companies_df = pd.DataFrame() #empty DF to append to

        page_iter = 1
        row_count = -1
        while(True):
            # Get the webpage after submitting the query to screen page
            screen_page = self.__session.get(self.__screen_url, params = screen_payload, headers=dict(Referer=screen_referer_url))
            #print(screen_page.url) #Prints the URL of the new web page

            # Extract the table into dataframe. skiprows is used to remove the un necessary rows
            table = pd.read_html(screen_page.text, index_col = 0, header = 0, skiprows = [16, 32, 48])[0] #table is a list
            no_of_rows = table.shape[0]

            # Updating the row_count using the number of rows from 1st page
            if(row_count == -1):
                row_count = no_of_rows
                if(row_count == 0):
                    return #TODO: Need to add a error here
            
            companies_df = pd.concat([companies_df, table], ignore_index = False)
            page_iter = page_iter + 1

            screen_referer_url = screen_page.url
            if(no_of_rows != row_count):
                break
            elif(companies_df.shape[0] >= self.__limit):
                companies_df = companies_df.loc[companies_df.index <= self.__limit]
                break
            else:
                screen_payload['page'] = str(page_iter)
            sleep(1)
        self.__companies = companies_df
    
    def getCompanies(self,refetch = False):
        if((self.__companies.empty == True) or (refetch == True)):
            self.__fetchCompanies()
        return self.__companies