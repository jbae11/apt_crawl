import numpy as np
from urllib.request import Request, urlopen
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import requests
import souper
import random

class proxy_ditto:
    """ Class for changing proxies """

    def __init__(self):
        self.proxy_dict = self.get_proxy_dict()
        self.proxy_list = list(self.proxy_dict.keys())
        print('Using from a list of %i proxies' %len(self.proxy_list))
        self.current_proxy = self.proxy_list[0]
        self.user_agent_list = self.get_user_agents()
        print('Using from a list of %i user agents' %len(self.user_agent_list))
        self.current_user_agent =self.user_agent_list[0]



    def morph_proxy(self):
        indx = random.randint(0, len(self.proxy_list))
        self.current_proxy = self.proxy_list[indx]


    def morph_user_agent(self):
        indx = random.randint(0, len(self.user_agent_list))
        self.current_user_agent = self.user_agent_list[indx]


    def get_proxy_dict(self):
        page_soup = souper.get_soup('https://free-proxy-list.net/')
        table = page_soup.findAll('table', {'id': 'proxylisttable'})
        proxy_dict = {}
        for row in table:
            row = row.tbody.findAll('tr')
            for columns in row:
                ip_port = columns.findAll('td')
                ip_port_list = []
                for i in ip_port[:2]:
                    ip_port_list.append(i.text)
                is_https = columns.findAll('td', {'class':'hx'})
                is_https = is_https[0].text
                if is_https == 'yes':
                    proxy_dict[ip_port_list[0] + ':' + ip_port_list[1]] = True
                else:
                    proxy_dict[ip_port_list[0] + ':' + ip_port_list[1]] = False
        return proxy_dict


    def get_user_agents(self):
        page_soup = souper.get_soup('http://www.useragentstring.com/pages/useragentstring.php?typ=Browser')
        result = []
        for ua in page_soup.findAll('li'):
            result.append(ua.text)
        return result