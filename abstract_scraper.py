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

class scraper:

    # settings and options
    def __init__(self, headless: bool=True, ublock: bool=True, timeout: int=10) -> webdriver.Firefox:
        wd = os.getcwd()
        FIREFOX_OPTIONS = webdriver.firefox.options.Options()
        if headless: FIREFOX_OPTIONS.add_argument('--headless')
        FIREFOX_OPTIONS.set_preference('browser.download.folderList', 2)
        FIREFOX_OPTIONS.set_preference('browser.download.dir', wd)
        firefox = webdriver.Firefox(options=FIREFOX_OPTIONS)
        if ublock: firefox.install_addon(os.path.join(wd, './uBlock0_1.49.2.firefox.signed.xpi'))
        firefox.implicitly_wait(timeout)
        
        self._firefox = firefox
        self._wd = wd
    
    # pulls all favs from ur nh.net favourites page
    def search(self, link: str, q: str='', max_pages = None, save_path: str='', v: bool=True) -> pd.DataFrame:
        try:
            # smart input parsing for links ppl will forget to put the http: or https:
            if not link.startswith('https://'):
                link = f'https://{link}'
            
            self.firefox.get(link)

            if v: print(f'SEARCHING {link} FOR: {q}')
            search = self.firefox.find_element(By.CSS_SELECTOR, '#query-input')
            search.send_keys(q)
            search.send_keys(Keys.RETURN)

            pgs = int(self.firefox.find_element(By.CSS_SELECTOR, '.page-top > ul > li:last-child > a').get_attribute('text'))
            if not max_pages: max_pages = pgs
            mangas = []
            for pg in range(1, pgs+1):
                if pg > max_pages: break
                link2 = f'{link}/search.html?{q}#{pg}'
                self.firefox.get(link2)

                links = [div.get_attribute('href') for div in self.firefox.find_elements(By.CSS_SELECTOR, '.gallery-content > div > a')]
                illustrators = [div.get_attribute('text') if div else np.nan for div in self.firefox.find_elements(By.CSS_SELECTOR, '.gallery-content > div > div.artist-list > ul > li:first-child > a')]
                titles = [div.get_attribute('title') if div else np.nan for div in self.firefox.find_elements(By.CSS_SELECTOR, '.gallery-content > div > h1 > a')]
                
                data = pd.DataFrame(zip_longest(links, titles, illustrators), columns=['link', 'title', 'illustrator'])
                mangas.append(data)
                if v: print(f'page: {pg} of {pgs}\n{data}')
                
            mangas = pd.concat(mangas, join='inner', axis=0)
            

            if not save_path: save_path = f'./{link.split("/")[2]}_{q}_{len(mangas)}.csv'
            if v: print(f'SAVING TO: {save_path}')
            mangas.to_csv(save_path, index=False, sep=',')
            return mangas
            
            # self.firefox.close()
        except Exception as e:
            print(f'ERROR {e}: something happened')


    # pulls all favs from ur nh.net favourites page
    def download(self, link: str, save_dir: str='doujins'):
        try:
            wd = os.getcwd()        
            self.firefox.get(link)


            download1 = self.firefox.find_element(By.CSS_SELECTOR, '#dl-button')
            self.firefox.execute_script("arguments[0].click();", download1)
            t.sleep(5)
            # no way to await the download so have to track it before navigating
            progress = 0 
            while not progress or progress < 100:
                progress = float(self.firefox.find_element(By.CSS_SELECTOR, '#progressbar').get_attribute('aria-valuenow'))
                print(progress)

            download_path = self.firefox.find_element(By.CSS_SELECTOR, '#gallery-brand > a').get_attribute('text')
            download_path = f'./{download_path}.zip'
            print(download_path)
            if not save_dir: os.path.mkdir(save_dir)
            save_path = f'./{save_dir}/{os.path.splitext(os.path.basename(download_path))[0]}'
            print(save_path)
            
            # subprocess.call(['unzip', download_path])
            


            # shutil.move(download_path, f'./{os.path.basename(download_path)}')

            # seems like cdn for image link the .avif blocks external requests sometimes not really sure so just gonna screenshot lol
            # img_link = firefox.find_element(By.CSS_SELECTOR, '#comicImages > picture > source').get_attribute('srcset')
            # _ = firefox.find_element(By.CSS_SELECTOR, '#comicImages')
            # fs.click()
            # fs.send_keys(Keys.ESCAPE)
    
            # firefox.save_screenshot(f'img1.png')


            
            
            # firefox.close()
        except Exception as e:
            print(f'ERROR {e}: something happened')

    @staticmethod
    def psites(sites: str='./sites.csv'):
        sites = pd.read_csv(sites, encoding='utf-8', sep=',')
        sites = tabulate(sites, headers='keys', tablefmt='simple', showindex=False)
        return sites

    def quit(self):
        self.firefox.quit()