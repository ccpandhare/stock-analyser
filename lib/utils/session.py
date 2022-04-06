import requests
import json
import os

# Creates a Screener session

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

    __session: requests.Session

    def __init__(self):
        #TODO: Remove un necessary stuff. See if we need to store theusername and password in class variables
        with open(os.path.join(os.path.dirname(__file__), '../../CREDENTIALS.json')) as f:
            data = json.load(f)
            self.__username = data['screener']['username']
            self.__password = data['screener']['password']
            self.__login()

    def __login(self):
        self.__session = requests.Session()
        self.__session.get(self.__login_url)
        csrftoken = self.__session.cookies['csrftoken']

        #Appending the csrftoken to the data payload
        login_payload = {'username':self.__username, 'password':self.__password, 'csrfmiddlewaretoken':csrftoken}
        self.__session.post(self.__login_url, data = login_payload, headers=dict(Referer=self.__login_url))
        
    def getSession(self) -> requests.Session:
        return self.__session

    def closeSession(self):
        self.__session.close()