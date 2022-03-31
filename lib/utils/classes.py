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