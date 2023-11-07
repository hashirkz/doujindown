# scraper for https://nhentai.to

import requests
from bs4 import BeautifulSoup
from itertools import zip_longest 
from tabulate import tabulate
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import is_color_like
import PIL


import shutil
import os
import time
import string
import re
from glob import glob
import datetime
import imghdr
from io import BytesIO

from abstract_scraper_bs4 import abstract_scraper

class nhentai_scraper(abstract_scraper):
    def __init__(self, _domain: str='https://nhentai.io'):
        super().__init__()
        self._DOMAIN = _domain
        self._SEARCH_ENDPOINT = f'{_domain}/search/?'

        # header needs cookies to access images on pgs
        self._HEADERS['Cookie'] = "eloquent_viewable=eyJpdiI6ImN1QU9jSE5CdVJvUENTajVudUNDMnc9PSIsInZhbHVlIjoiKzR2U1lNVGhFTGh0KzVCZFdQZ2dzODVwbzA0SHoxV2ZzZFYwQUgzamJJTHk1Q3d5Z1c5eWZVOWprR1FVTEptMDArbUlIWlZxMXRubkFqdzRjeEplUDM3b2FsMGdnZmFyM1grY3dQSDMwVmYvZVI0ZksyeUVkaHhCcWwyK1NRM04iLCJtYWMiOiJiNmU0MjRkNDYwNmNjODQ1YWJhZTMwYjkxMDZkZTNmZmYyYzk1ZGFiOTk5ZmI5YmU2N2Q2MThmMjNkNTg4NjE2In0%3D; XSRF-TOKEN=eyJpdiI6InBDejBWRXBwSGkycVhqTGVoUnJsRFE9PSIsInZhbHVlIjoiV0hhUWp1MUg5eW4yaEVBaFliZ0NsNWZXT2VIMzQxeTNjYldtYnZXbllPL2d4Rm1aYktvelc1Y2lHQ3lpaGVxQiIsIm1hYyI6ImNjMjY3MDY0YzE5NjM3Y2MwMjczNmQ5OWM2ZmMxMWZiZDBkMmRiZGRkYzIyMWRlNTg2MzZkMzQ2YTY3NGQwYmQifQ%3D%3D; nhentai_session=eyJpdiI6IlNHV2ppRVF6d085TERpOXltcUFTeWc9PSIsInZhbHVlIjoiUnhxbDRKSnFRelVkZmZZei9MVFN0elVYYkQyWXYrQkROekxGQUxzc0RhOW9xbDNmeHAyc2taQ2VtYXpXWGkyMSIsIm1hYyI6IjlhYTYzNDI0MWQ0NWNiYjk2YWU1ZGRiZGQ5ZmIxNThlODhmODVkY2NjOWMxYTJiMjc4MWJmMmY3MmM4NjNmOGEifQ%3D%3D"


    # search query on manganelo
    def search(
        self, 
        q: str='', 
        max_pgs: int = 5, 
        save: bool=False,
        manga_title_css: str='.search-story-item .item-img'):

        url = 'https://nhentai.to/g/195266/'
        resp = requests.get(url, headers=self._HEADERS)
        print(resp.status_code)
        # print('WARNING: *as 08/24/2023\nseems like ww6.manganelo.tv has a broken search function so any page >= 2 is just a copy of the page 1')
        # mangas = []
        # # search uptill max_pgs for manga titles
        # for pg in range(max_pgs):

        #     # query search endpoint
        #     url = f'{self._SEARCH_ENDPOINT}/{q}?page={pg+1}'
        #     soup = self.soupify(url)
        #     titles = list(map(lambda e : e['title'], soup.select(manga_title_css)))
        #     links = list(map(lambda e : f'{self._DOMAIN}{e["href"]}', soup.select(manga_title_css)))

        #     for title, link in zip(titles, links):
        #         mangas.append({
        #             'manga_title': title,
        #             'manga_link': link})
            

        # mangas = pd.DataFrame(mangas).astype(str).drop_duplicates()
        # print(f'num results: {len(mangas)}\n{mangas}\n')

        # if save:
        #     formatted_date = datetime.date.today().strftime('%m_%d_%Y')
        #     savep = f'{os.path.basename(self._DOMAIN).split(".")[0]}{formatted_date}'
        #     print(f'saving to {savep}')
        #     mangas.to_csv(savep, index=False)

        # return mangas

    # download imgs/pgs to pdf from manganelo chapter link
    def download_chapter(
        self, 
        link: str, 
        save_dir: str='',
        wait_for_default: int=0,
        format:str='zip',
        ch_num: str='',
        use_cbz: bool=True,
        imgs_css: str='img.img-loading',
        thumbnail_css: str='.thumb-container'):

        url = 'https://cdn.dogehls.xyz/galleries/1063632/1.png'
        resp = requests.get(url, headers=self._HEADERS)
        print(resp.status_code)
        # soup = self.soupify(link)
        # pgs = len(soup.select(thumbnail_css))

        # for pg in range(pgs):
        #     url = f'{link}/{pg+1}'
        #     soup = self.soupify(url)
            

    # view chapter list
    def chapters(
        self, 
        link: str, 
        save: bool=False,
        chapters_css: str='.row-content-chapter .a-h .chapter-name',
        num_views_css: str='.row-content-chapter .a-h .chapter-view',
        date_css: str='.row-content-chapter .a-h .chapter-time',
        manga_title_css: str='.story-info-right h1'):

        # extract titles + links using selector parameters from soup
        soup = self.soupify(link)
        manga_name = soup.select_one(manga_title_css).text        
        chapter_titles = list(map(lambda e: e.text, soup.select(chapters_css)))
        chapter_links = list(map(lambda e: f"{self._DOMAIN}{e['href']}", soup.select(chapters_css)))
        num_views = list(map(lambda e: e.text, soup.select(num_views_css)))
        upload_date = list(map(lambda e: self.soft_clean(e.text), soup.select(date_css)))
    
        chapters = pd.DataFrame({
            'chapter_title': chapter_titles,
            'chapter_link': chapter_links,
            'num_views': num_views,
            'upload_date': upload_date,
        })        

        print(f'name: {manga_name}\nNUM RESULTS: {len(chapters)}\n{chapters}')

        if save:
            formatted_date = datetime.date.today().strftime('%m_%d_%Y')
            savep = f'{os.path.basename(link)}{formatted_date}'
            print(f'saving to {savep}')
            chapters.to_csv(savep, index=False)
        
        self._chapters = chapters
        return chapters


if __name__ == '__main__':
    nhentai = nhentai_scraper()
    nhentai.download_chapter('https://nhentai.to/g/195266')
