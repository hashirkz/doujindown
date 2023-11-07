import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import pandas as pd
from abc import ABC, abstractmethod


import os
import time
import string
import re
from glob import glob

class abstract_scraper(ABC):
    _HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Windows",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Content-Encoding": "utf-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }


    def __init__(self, _headers: dict=None, wait_rl: int=2):
        self._wait_rl= wait_rl
        self._HEADERS = __class__._HEADERS if not _headers else _headers
        self._chapters = []
        self._manga = ''

    
    # handling boilerplate to request and get soup back
    def soupify(self, link: str, show_status: bool=True, max_rls: int=100, show_soup: bool=False) -> BeautifulSoup:
        print(f'\nSEARCHING: {link}')

        resp = requests.get(link, headers=__class__._HEADERS)
        # dealing with forbidden/nopage http response errors
        if resp.status_code == 404:
            print(f'ERROR 404 NOT FOUND: page does not exist {link}')
            return
        
        elif resp.status_code == 403:
            print(f'ERROR 403 FORBIDDEN: unable to access page {link}')
            return 
        
        # waiting on rate limit default 2 min wait
        wait = time.time()
        num_rls = 0
        while resp.status_code == 429:
            print(f'RATE LIMITED: {time.time()-wait}')
            time.sleep(self._wait_rl * 60)
            resp = requests.get(link, headers=__class__._HEADERS)

            # exiting if max rate limits has been reached
            if num_rls == max_rls: 
                print(f'EXITING:\nmax number of rate limits reached: {max_rls}')
                return

            num_rls += 1

        soup = BeautifulSoup(resp.text, 'html.parser')
        if show_status: print(f'HTTP STATUS: {resp.status_code}\n')
        if show_soup: print(f'SHOWING SOUP: {soup.prettify()}\n')
        return soup

    # search for query at website search endpoint
    @abstractmethod
    def search(
        self, 
        q: str='', 
        max_pgs: int = 5, 
        save: bool=False,
        manga_title_css: str='.search-story-item .item-img') -> pd.DataFrame:
        pass


    # download imgs/pgs to pdf from chapter link
    @abstractmethod
    def download_chapter(
        self, 
        link: str, 
        save_dir: str='',
        wait_for_default: int=0,
        format:str='zip',
        ch_num: str='',
        use_cbz: bool=True,
        imgs_css: str='img.img-loading') -> None:
        pass


    # view chapter list
    @abstractmethod
    def chapters(
        self, 
        link: str, 
        save: bool=False,
        chapters_css: str='.row-content-chapter .a-h .chapter-name',
        num_views_css: str='.row-content-chapter .a-h .chapter-view',
        date_css: str='.row-content-chapter .a-h .chapter-time',
        manga_title_css: str='.story-info-right h1') -> pd.DataFrame:
        pass

    # void dowloads all chapters from link if self._chapters is empty
    def download_chapters(
        self, 
        link: str=None, 
        save_dir: str='./mangas', 
        download_range: str='') -> None:

        if not link and len(self._chapters) == 0:
            print(f'NOTHING TO DOWNLOAD:\nif this is unexpected try using {__class__.__name__}.chapters(<insert manga link>) to fill the cached or provide a link')
            return 
        
        if link: self.chapters(link)

        if len(self._chapters) == 0:
            print(f'ERROR: found nothing to download in cache or at {link}')
            return

        print('SEARCHING CACHED FILES')

        # parsing range if user passed in some range
        match = re.match("(\d*)-?(\d*)", download_range)
        start = int(match.group(1))-1 if match.group(1) else 0
        end = int(match.group(2)) if match.group(2) else len(self._chapters)

        print(f'saving to {save_dir}')
        for i, ch in enumerate(self._chapters['chapter_link'].iloc[start:end]):
            print(f'downloading ch: {start+i+1}/{len(self._chapters)}')
            self.download_chapter(ch, save_dir, ch_num=start+i+1)
        return
    
    # so we can use scraper polymorphically 
    # better solution to create abstract class more general than _sel and _bs4 and add abstract method .quit there
    def quit() -> None:
        return
    
    # pretty prints sites message
    @staticmethod
    def psites(sites: str='./sites.csv') -> str:
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
