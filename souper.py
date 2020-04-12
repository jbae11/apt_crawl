import numpy as np
from urllib.request import Request, urlopen
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import requests
from itertools import cycle
import proxy_ditto
import time


user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'

def get_soup(url, randomize_proxy=False,
             user_agent=user_agent):
    with requests.Session() as s:
        s.headers['User-Agent'] = user_agent
        response = s.get(url)
        page_soup = soup(response.text, 'html.parser')
        return page_soup


def get_soup_proxy_ditto(url, prx_ditto_obj,
                         pause=0):
    while True:
        time.sleep(pause)
        try:
            proxies = {'http': prx_ditto_obj.current_proxy,
                       'https': prx_ditto_obj.current_proxy}
            with requests.Session() as s:
                s.headers['User-Agent'] = prx_ditto_obj.current_user_agent
                proxies = {'http': prx_ditto_obj.current_proxy,
                           'https': prx_ditto_obj.current_proxy}
                print('Getting response from:\n\t%s'%url)
                response = s.get(url, proxies=proxies)
                # recursively run with another proxy if blocked
                if response.status_code != 200:
                    print('Blocked?? Status code is ', response.status_code)
                    # if we raise an error here, it goes to except
                    raise ValueError
                else:
                    print('Successfully got response from:\n\t%s'%url)
                page_soup = soup(response.text, 'html.parser')
                prx_ditto_obj.morph_proxy()
                prx_ditto_obj.morph_user_agent()
                return page_soup
        except:
            print('Proxy', prx_ditto_obj.current_proxy, 'did not work')
            prx_ditto_obj.morph_proxy()
            prx_ditto_obj.morph_user_agent()