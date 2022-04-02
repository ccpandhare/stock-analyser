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

    def __init__(self, ticker: str):
        self.ticker = ticker

    def DCF_MC_analysis(self):
        
    def calc_NPV(self, init_profit, init_profit_growth_rate, perpetual_growth_rate, \
                years_until_decay, discount_rate, init_capex_rate, market_cap, no_of_years):
        """
        Usage:
        1. Calculate the Net Present Value depending upon csh flows
        2. init_profit = {CFO, OP - Tax paid (this is better)}
        3. init_profit_growth_rate = can be list of gaussian distributions with 3 different means
                                     The center mean can be an average of the last 3 years while 
                                     upper and lower can be +/-4%
        4. Perpetual growth rate = can be estimate of inflation
        5. years_until_decay = time till which company would grow at a rate higher than perpetual
                                growth rate
        6. discount_rate = assume a high discount rate
        7. init_capex_rate = get the capex of last 3-4 years and then use it 
        8. market cap
        9. no of years = real holding time of the investment
        """
        # Linear decay factor 
        decay_factor = (init_profit_growth_rate - perpetual_growth_rate)/years_until_decay

        # During the perpetual growth, no capex would be done. Linear decay in the capex
        capex_decay_factor = (init_capex_rate)/years_until_decay
        net_present_value = 0
        profit = init_profit #base profit
        for year in range(0, no_of_years):
            if(year<years_until_decay):
                #Calculate the profit growth & capex rate for each year
                pgr = init_profit_growth_rate - (decay_factor*year)
                capex_rate = init_capex_rate - (year+1)*capex_decay_factor
            else:
                pgr = perpetual_growth_rate
                #capex_rate = perpetual_growth_rate #maintainence capex#
                capex_rate = 0.0
            
            #calculate the profit as well as discounted profit
            profit = profit*(1+pgr) #assuming that 20% of CFO for that year is spent on capex and acquisitions
            discounted_profit = (profit*(1-capex_rate))/(pow((1+discount_rate),(year+1)))
            net_present_value += discounted_profit

        terminal_value = profit*(1+perpetual_growth_rate)/(discount_rate-perpetual_growth_rate)
        discounted_terminal_value = terminal_value/(pow((1+discount_rate),(year+1)))
        net_present_value += discounted_terminal_value
        #print(net_present_value)
        return (market_cap/net_present_value)
    
    def calc_NPV_distribution(self, init_profit, init_profit_growth_rate, perpetual_growth_rate, \
                              years_until_decay, discount_rate, init_capex_rate, market_cap, \
                              no_of_years, iterations):
        ipgr_len = len(init_profit_growth_rate)
        npv_distribution = []
        for yud in years_until_decay:
            for pgr in perpetual_growth_rate:
                for j in range(iterations):
                    npv_distribution.append(self.calc_NPV(init_profit, init_profit_growth_rate[i][j], pgr, yud, discount_rate[j], init_capex_rate, market_cap)) 
        return npv_distribution



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