# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.common.exceptions import * 

# from bs4 import BeautifulSoup
# from urllib.request import Request, urlopen
# from urllib3 import 
from itertools import zip_longest 
from tabulate import tabulate
import pandas as pd
import numpy as np

import os
import urllib.parse
import time as t
import json
# import zipfile
# import subprocess

from doujin_scrapers.abstract_scraper_bs4 import abstract_scraper
from doujin_scrapers.hitomi import hitomila_scraper
from doujin_scrapers.manganelo import manganelo_scraper

# reading scraper registry - maps websites to scrapers
def read_json(path: str) -> dict:
    with open(path, 'r') as registry_file:
        json_dict = json.loads(registry_file.read())

    if not json_dict: 
        print(f'ERROR: empty {path} please add the sites and their associated scrapers as k, v pairs')
        raise ValueError
    
    return json_dict

# pretty message for app entry
def msg():
    msg = ''
    violet = '\033[38;5;105m'
    violet2 = '\033[38;5;63m'
    white = '\033[0m'
    with open ('./doujindown.txt', 'r') as txtfile:
        doujindown = txtfile.read()

    msg = violet + doujindown + violet2 + '\n' + abstract_scraper.psites() + white + '\n'
    print(msg)

# main app function
def app():

    link = input('? LINK TO CHAPTER / CHAPTERS: ').lower().strip()
    download_range = input('? CHAPTERS TO DOWNLOAD default to all or enter inclusive range i.e 1-40: ').lower().strip()
    
    
    # lookup domain in site_registry.json
    # pattern = r"https?://(www\.[a-zA-Z0-9.-]+).*"
    # updating domain to the scrapable mirror
    # mirrors = read_json('./mirrors.json')
    # if domain in mirrors:
    #     domain = domain._replace(netloc = mirrors.get(domain))
    domain = urllib.parse.urlparse(link).netloc
    scraper = read_json('./registry.json').get(domain)

    # unable to find domain in the site registry
    if not scraper: 
        print(f'ERROR: unsupported link from: {domain}')
        return 1

    try:
        # if the lookup is successful create the scraper subclass object for whatever website link was
        # e.x user inputs ww7.manganelo.tv link then generate a manganelo_scraper object *factory design
        scraper = globals()[scraper]()
        # scraper.chapters(link)
        scraper.download_chapters(link=link, download_range=download_range)

    except Exception as e:
        print(f'ERROR:\n{e}')

    app()
    # if link == 'hitomi.la':
    #     hitomi_la = hitomila_scraper()

    #     op = input(options).strip().lower()
    #     if op == 'search':
    #         q = input('SEARCH FOR: ').lower().strip()
    #         max_pgs = input('max num of pgs to search: ').lower().strip()
    #         if max_pgs: max_pgs = int(max_pgs)
        
    #         hitomi_la.search(link, q=q, max_pages=max_pgs)

    #     elif op == 'download':
    #         link = input('DOUJIN LINK: ')

    #         hitomi_la.download(link)

    #     hitomi_la.quit()

        # link = 'https://hitomi.la/manga/lovely-aina-chan-2-%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-2131636.html#1'
        # download(firefox, link)

        # t.sleep(10)


    # link = 'https://hitmoi.la'
    # search(firefox, link, 'kyockcho')
    # request.urlopen(request.Request(link, headers={'User-Agent':'Mozilla/5.0'}))

if __name__ == '__main__':
    msg()
    app()
    # registry = read_scraper_registry()
    # registry_repr = tabulate(pd.DataFrame.from_dict(registry, orient="index"), headers = 'keys', tablefmt='simple')
    # print(registry_repr)
    # manganelo = manganelo_scraper()
    # manganelo.chapters('https://manganato.com/manga-hn951948')