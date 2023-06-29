import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import urllib
import re
import os
import time as t

# void func to update pages.csv to remove all pages with duplicate nhids 
# preserves order
def remove_dup_nhid(path: str) -> np.ndarray:
    nh_pages = pd.read_csv(path)
    nh_ids = nh_pages["nhid"].to_numpy()
    _, i = np.unique(nh_ids, return_index=True)
    nh_ids = nh_ids[np.sort(i)]
    n = nh_ids.shape[0]
    nh_ids.reshape(1,n)
    pd.DataFrame(nh_ids).to_csv('nh_ids.csv', header=None, index=None)

    return nh_ids

# reads csv of nh data into numpy ndarary
def read_nh(path: str='nh_ids.csv') -> np.ndarray:
    return pd.read_csv(path).to_numpy()

# updates nh_ids.csv to include other information for nhids
# webscraping w selenium
def update_info(nh: np.ndarray) -> pd.DataFrame:
    data = []
    records = 0
    num_records = nh.shape[0]
    # nhentai has cloudflare so its basically impossible to use selenium / beautifulsoup for this idk what to do tbh
    for nhid in nh[:, 0]:
        # formated link to nhentai.to cant use .net cause of cloudflare but will save the true link as .net
        save_link = f'https://nhentai.net/g/{nhid}'
        link = f'https://nhentai.to/g/{nhid}'

        try:
            # request page and build beautiful soup parser
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = Request(link, headers=hdr)
            page = urlopen(req)
            soup = BeautifulSoup(page, features='lxml')
        except urllib.error.HTTPError:
            continue


        # select attributes via css selectors
        name = soup.select('#info > h1')[0].text.strip()
        tags = soup.select('#tags')
        illustrator, character = 'null', 'null'
        for div in tags:
            match_artist = re.search(r'Artists\s*\n*([a-zA-Z]+\s*[a-zA-Z]+)', div.text)
            if match_artist: 
                illustrator = match_artist.group(1)
                break

        for div in tags:
            match_character = re.search(r'Characters\s*\n*([a-zA-Z]+\s*[a-zA-Z]+)', div.text)
            if match_character: 
                character = match_character.group(1)
                break      
        data.append([nhid, name, save_link, illustrator, character])

        # just to see progress
        record += 1
        print(f'updated record: {record}/{num_records}')

    data = np.array(data)
    return pd.DataFrame(data)


# def update_fav(nh: np.ndarray, user: str=None, password: str=None):
#     pass

if __name__ == '__main__':
    pass
    # reads numbers and formats stuff_nh.csv
    # nh = read_nh()
    # a = update_info(nh)
    # print(a)
    # a.to_csv('stuff_nh.csv', header=None, index=None)

    # stuff_nh = pd.read_csv('./stuff_nh.csv')
    # print(stuff_nh)
