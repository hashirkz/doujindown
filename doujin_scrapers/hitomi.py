from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import * 


from itertools import zip_longest 
from tabulate import tabulate
import pandas as pd
import numpy as np


import os
import time as t
import shutil
import sys

from .abstract_scraper_sel import abstract_scraper


class hitomila_scraper(abstract_scraper):

    def __init__(self, _domain: str='https://hitomi.la'):
        super().__init__()
        self._DOMAIN = _domain
        self._SEARCH_ENDPOINT = f'{_domain}/search.html?'

    # queries hitomi.la for whatever query and searches uptill max_pgs or last_pg
    def search(
        self, 
        q: str='', 
        max_pgs: int = 100, 
        save_path: str='', 
        save: bool=False,
        pgs_css: str='.page-top ul li:last-child a',
        manga_title_css: str='.gallery-content div h1 a',
        manga_illustrator_css:str='.gallery-content > div > div.artist-list > ul > li:first-child > a') -> pd.DataFrame:

        try:
            mangas = []
            last_pg = max_pgs
            pg = 0
            while pg < last_pg and pg < max_pgs:
                url = f'{self._DOMAIN}/search.html?{q}#{pg+1}'
                self._firefox.get(url)

                # find the last indexed page if the current page is page 0 *pg 1 really
                if pg == 0:
                    last_pg = int(self._firefox.find_element(By.CSS_SELECTOR, pgs_css).text)

                print(f'SEARCHING: pg: {pg+1}/{last_pg} at url: {url}')

                titles = list(map(lambda e : e.text if e else None, self._firefox.find_elements(By.CSS_SELECTOR, manga_title_css)))
                urls = list(map(lambda e : e.get_attribute('href') if e else None, self._firefox.find_elements(By.CSS_SELECTOR, manga_title_css)))
                illustrators = list(map(lambda e : e.text if e else None, self._firefox.find_elements(By.CSS_SELECTOR, manga_illustrator_css)))

                for title, link, illustrator in zip_longest(titles, links, illustrators):
                    mangas.append({
                        'title': title,
                        'link': link,
                        'illustrator': illustrator
                    })
                
                pg += 1
                
                
            mangas = pd.DataFrame.from_dict(mangas)     
            print(f'{len(mangas)} results:\n{mangas}')

            if save:
                if not save_path: save_path = f'./{self._DOMAIN.split("/")[2]}_{q}_{len(mangas)}.csv'
                print(f'SAVING TO: {save_path}')
                mangas.to_csv(save_path, index=False, sep=',')
            
            return mangas
            
        except Exception as e:
            print(f'ERROR {e}: something happened')


    # really need to update this its a very hacky way to download using the download button bad lol
    # downloads manga from url to savedir
    def download_chapters(
        self, 
        link: str=None, 
        save_dir: str='./doujins',
        download_range: str='') -> None:

        try:
            self._firefox.get(link)

            download1 = self._firefox.find_element(By.CSS_SELECTOR, '#dl-button')
            self._firefox.execute_script("arguments[0].click();", download1)
            t.sleep(2)

            # no way to await the download so have to track it before navigating
            progress = 0 
            while not progress or progress < 100:
                progress = float(self._firefox.find_element(By.CSS_SELECTOR, '#progressbar').get_attribute('aria-valuenow'))
                # shows progress update and flushes last message so it doesnt print a lot of lines
                print(progress)
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")


            download_path = self.soft_clean(self._firefox.find_element(By.CSS_SELECTOR, '#gallery-brand > a').get_attribute('text') + '.zip', space_to_underscore=True, remove_weird=True, lower=True)
            download_path = os.path.join(os.getcwd(), download_path)
            if save_dir and not os.path.exists(save_dir): os.mkdir(save_dir)
            t.sleep(2)
            shutil.move(download_path, os.path.join(save_dir, os.path.splitext(os.path.basename(download_path))[0] + '.cbz'))

        except Exception as e:
            print(f'ERROR {e}: something happened')
        
if __name__ == '__main__':
    hitomi = hitomila_scraper()
    # hitomi.search(q='kyockcho')
    hitomi.download('https://hitomi.la/doujinshi/nico-joku-%E4%B8%AD%E6%96%87-172711-970949.html#1')
    hitomi.quit()
    