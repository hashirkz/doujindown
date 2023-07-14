from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import * 

# from urllib3 import request
# from bs4 import BeautifulSoup
# from urllib.request import Request, urlopen
from itertools import zip_longest 
from tabulate import tabulate
import pandas as pd
import numpy as np

import os
import time as t
import zipfile
import subprocess

from doujin_scrapers.abstract_scraper import manga_scraper
from doujin_scrapers.hitomi_la import hitomi_la_scraper



# main app function
def app():
    msg = ''
    with open ('./doujindown.txt', 'r') as txtfile:
        doujindown = txtfile.read()
    violet = '\033[38;5;105m'
    violet2 = '\033[38;5;63m'
    white = '\033[0m'

    msg = violet + doujindown + violet2 + '\n' + manga_scraper.psites() + white + '\n'
    options = 'OPTIONS\nsearch: search websites for doujins\ndownload: download doujins from site\nchoose: '
    print(msg)


    link = input('SITE: ').lower().strip()
    if link == 'hitomi.la':
        hitomi_la = hitomi_la_scraper()

        op = input(options).strip().lower()
        if op == 'search':
            q = input('SEARCH FOR: ').lower().strip()
            max_pgs = input('max num of pgs to search: ').lower().strip()
            if max_pgs: max_pgs = int(max_pgs)
        
            hitomi_la.search(link, q=q, max_pages=max_pgs)

        elif op == 'download':
            link = input('DOUJIN LINK: ')

            hitomi_la.download(link)

        hitomi_la.quit()

        # link = 'https://hitomi.la/manga/lovely-aina-chan-2-%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-2131636.html#1'
        # download(firefox, link)

        # t.sleep(10)


    # link = 'https://hitmoi.la'
    # search(firefox, link, 'kyockcho')
    # request.urlopen(request.Request(link, headers={'User-Agent':'Mozilla/5.0'}))

if __name__ == '__main__':
    app()