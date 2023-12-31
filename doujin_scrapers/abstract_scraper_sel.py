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
import re
import string
from abc import ABC, abstractmethod

class abstract_scraper(ABC):

    # boilerplate settings and options
    def __init__(
        self, 
        headless: bool=True, 
        ublock: bool=True, 
        timeout: int=10) -> webdriver.Firefox:
        wd = os.getcwd()
        FIREFOX_OPTIONS = webdriver.firefox.options.Options()
        if headless: FIREFOX_OPTIONS.add_argument('--headless')
        FIREFOX_OPTIONS.set_preference('browser.download.folderList', 2)
        FIREFOX_OPTIONS.set_preference('browser.download.dir', wd)
        firefox = webdriver.Firefox(options=FIREFOX_OPTIONS)
        if ublock: firefox.install_addon(os.path.join(wd, 'uBlock0_1.49.2.firefox.signed.xpi'))
        firefox.implicitly_wait(timeout)
        
        self._firefox = firefox
        self._wd = wd

    def quit(self):
        self._firefox.quit()

    @abstractmethod
    def search(
        self, 
        q: str='', 
        max_pgs: int = 100, 
        save_path: str='', 
        save: bool=False,
        pgs_css: str='.page-top ul li:last-child a',
        manga_title_css: str='.gallery-content div h1',
        manga_illustrator_css:str='.gallery-content > div > div.artist-list > ul > li:first-child > a') -> pd.DataFrame:
        pass

    # @abstractmethod
    # def chapters():
    #     pass

    @abstractmethod
    def download_chapters(
        self, 
        link: str=None, 
        save_dir: str='./doujins',
        download_range: str='') -> None:
        pass



    @staticmethod
    def psites(sites: str='./sites.csv'):
        sites = pd.read_csv(sites, encoding='utf-8', sep=',')
        sites = tabulate(sites, headers='keys', tablefmt='simple', showindex=False)
        return sites

    # cleaning utility functions
    @staticmethod
    def hard_clean(text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = text.replace('\n', ' ')
        text = re.sub(r'http.*', '', text)
        text = text.strip(string.punctuation + string.whitespace)
        return text

    @staticmethod
    def soft_clean(text: str, allow_commas: bool=True, space_to_underscore: bool=False, lower: bool=False, remove_weird: bool=False) -> str:
        text = re.sub(r"[\n'\"]", '', text) if allow_commas else re.sub(r"[\n'\",]", '', text)
        text = text.strip(string.whitespace)
        if space_to_underscore: text = re.sub(r" ", '_', text)
        if lower: text = text.lower()
        if remove_weird: text = re.sub(r'[^\w\s]', '', text)
        return text