import pandas as pd
import numpy as np
from selenium import webdriver
from urllib3 import request

FIREFOX_OPTIONS = webdriver.firefox.options.Options()
# FIREFOX_OPTIONS.add_argument('headless')

# pulls all favs from ur nh.net favourites page
def pull_favs(link: str, save_path: str='', v: bool=True) -> pd.DataFrame:
    
    firefox = webdriver.Firefox(options=FIREFOX_OPTIONS)
    firefox.get(link)
    print(firefox)
    firefox.close()


if __name__ == '__main__':
    link = 'https://github.com/hashirkz'
    # pull_favs(link)
    request.urlopen(request.Request(link, headers={'User-Agent':'Mozilla/5.0'}))