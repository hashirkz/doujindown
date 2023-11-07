# scraper for https://ww6.manganelo.tv

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

from .abstract_scraper_bs4 import abstract_scraper

class manganelo_scraper(abstract_scraper):

    def __init__(self, _domain: str='https://ww6.manganelo.tv'):
        super().__init__()
        self._DOMAIN = _domain
        self._SEARCH_ENDPOINT = f'{_domain}/search'


    # search query on manganelo
    def search(
        self, 
        q: str='', 
        max_pgs: int = 5, 
        save: bool=False,
        manga_title_css: str='.search-story-item .item-img'):

        print('WARNING: *as 08/24/2023\nseems like ww6.manganelo.tv has a broken search function so any page >= 2 is just a copy of the page 1')
        mangas = []
        # search uptill max_pgs for manga titles
        for pg in range(max_pgs):

            # query search endpoint
            url = f'{self._SEARCH_ENDPOINT}/{q}?page={pg+1}'
            soup = self.soupify(url)
            titles = list(map(lambda e : e['title'], soup.select(manga_title_css)))
            links = list(map(lambda e : f'{self._DOMAIN}{e["href"]}', soup.select(manga_title_css)))

            for title, link in zip(titles, links):
                mangas.append({
                    'manga_title': title,
                    'manga_link': link})
            

        mangas = pd.DataFrame(mangas).astype(str).drop_duplicates()
        print(f'num results: {len(mangas)}\n{mangas}\n')

        if save:
            formatted_date = datetime.date.today().strftime('%m_%d_%Y')
            savep = f'{os.path.basename(self._DOMAIN).split(".")[0]}{formatted_date}'
            print(f'saving to {savep}')
            mangas.to_csv(savep, index=False)

        return mangas

    # download imgs/pgs to pdf from manganelo chapter link
    def download_chapter(
        self, 
        link: str, 
        save_dir: str='',
        wait_for_default: int=0,
        format:str='zip',
        ch_num: int=0,
        use_cbz: bool=True,
        imgs_css: str='img.img-loading',
        print_img_links: bool=False):

        soup = self.soupify(link)
        chapter_name = soup.select_one(imgs_css)['alt']

        print(f'CHAPTER NAME: {chapter_name}')

        # if we searched this manga and cached its name save to the directory named self._manga
        if self._manga: save_dir = os.path.join(save_dir, self._manga)
        
        pgs = list(map(lambda e: e['data-src'],soup.select(imgs_css)))
        print(f'NUM PGS FOUND: {len(pgs)}')

        for pg_num, pg in enumerate(pgs):
            resp = requests.get(pg, headers=self._HEADERS)

            # handling rate limits and waiting to avoid cloudflare detection stuff
            wait = time.time()
            while resp.status_code == 429:
                print(f'RATE LIMITED: {time.time() - wait}m')
                time.sleep(self._wait_rl * 60)
                resp = requests.get(pg, headers=self._HEADERS)

            # error handling but not well lol only accept http 200 responses
            if resp.status_code != 200:
                print(f'ERROR BAD HTTP STATUS: {resp.status_code}\nUNABLE TO RETREIVE\nPG: {pg_num}/{len(pgs)}\nFROM: {pg}')
                continue
            
            if print_img_links: print(f'reading {pg}: {pg_num+1}/{len(pgs)}')

            try:
                # read img data *guesses format of data
                img_bytes = BytesIO(resp.content)
                fmt = imghdr.what(img_bytes) 
                if not fmt: fmt = 'jpg'
                img = plt.imread(img_bytes, format=fmt)

            except PIL.UnidentifiedImageError as e:
                print(f'{e}: UNABLE TO READ {pg}')
                continue

            
            if save_dir and not os.path.exists(save_dir):
                print(f'creating directory: {save_dir} in {os.getcwd()}')
                os.mkdir(save_dir)

            basename = f'{ch_num}_{self.soft_clean(chapter_name, space_to_underscore=True, lower=True, remove_weird=True)}'
            if not os.path.exists(os.path.join(save_dir, basename)): os.mkdir(os.path.join(save_dir, basename))

            savep = os.path.join(save_dir, basename, f'pg_{pg_num}.{fmt}')
            
            plt.imsave(savep, img) if is_color_like(img) else plt.imsave(savep, img, cmap='gray')

            if wait_for_default:
                if print_img_links: print(f'sleeping for: {wait_for_default}m')
                time.sleep(wait_for_default)

        shutil.make_archive(os.path.join(save_dir, basename), format, os.path.join(save_dir, basename))
        shutil.rmtree(os.path.join(save_dir, basename))

        if use_cbz: 
            os.rename(os.path.join(save_dir, f'{basename}.{format}'), f'{os.path.join(save_dir, basename)}.cbz')
            

    # view chapter list
    def chapters(
        self, 
        link: str, 
        save: bool=False,
        chapters_css: str='.row-content-chapter .a-h .chapter-name',
        num_views_css: str='.row-content-chapter .a-h .chapter-view',
        date_css: str='.row-content-chapter .a-h .chapter-time',
        manga_title_css: str='.story-info-right h1',
        mdy_time_format: str='%b %d,%y'):

        # extract titles + links using selector parameters from soup
        soup = self.soupify(link)
        manga_name = soup.select_one(manga_title_css).text        
        self._manga = manganelo_scraper.soft_clean(manga_name, space_to_underscore=True, lower=True)
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

        # chapters['upload_date'] = pd.to_datetime(chapters['upload_date'], format=mdy_time_format)    
        # chapters = chapters.sort_values(by='upload_date', ascending=True) 
        #  
        # reversing chapters df  
        chapters = chapters.iloc[::-1].reset_index(drop=True)

        print(f'name: {manga_name}\nNUM RESULTS: {len(chapters)}\n{chapters}')

        if save:
            formatted_date = datetime.date.today().strftime('%m_%d_%Y')
            savep = f'{os.path.basename(link)}{formatted_date}'
            print(f'saving to {savep}')
            chapters.to_csv(savep, index=False)
        
        self._chapters = chapters
        return chapters


if __name__ == '__main__':
    manganelo = manganelo_scraper()

    # link = 'https://ww6.manganelo.tv/manga/manga-na952709'
    # manganelo.download_chapters(link, save_dir='../mangas/made_in_abyss', skip_first_n=23)

    # link = 'https://ww6.manganelo.tv/manga/manga-cp980050'
    # manganelo.download_chapters(link, save_dir='../mangas/toilet_bound_hanako_kun', skip_first_n=5)

    # manganelo.search('the promised neverland')
    # link = 'https://ww6.manganelo.tv/manga/manga-hn951948'
    # manganelo.chapters(link)
    # manganelo.download_chapters(link, save_dir='../mangas/mahou_soujo_site', skip_first_n=80)

    # link = 'https://ww6.manganelo.tv/manga/manga-vl972446'
    # link = 'https://ww6.manganelo.tv/manga/manga-cp980050'
    link = 'https://ww7.manganelo.tv/manga/manga-vp972424'
    manganelo.download_chapters(link, save_dir='../mangas/kenja_no_deshi_wo_nanoru_kenja')
