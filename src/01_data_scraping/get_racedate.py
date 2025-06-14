import re
import time
import datetime
import os

import requests
import pandas as pd
from bs4 import BeautifulSoup

from data_scraping_module import get_racedate_list


def main():

    save_dir = "data/race_date"
    year_list = [
        # 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 
        2010, 2011, 2012, 2013, 2014, 2015, 2016,2017, 2018, 2019, 2020, 
        2021, 2022, 2023
        ]  # 保存する年のリスト
    month_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] 

    for year in year_list:
        print(f"Processing year: {year}")
        race_date_list = []
        for month in month_list:
            race_date_list.extend(get_racedate_list(year, month))
            time.sleep(1)  # Sleep to avoid overwhelming the server

        # 重複を除去
        race_date_list = sorted(set(race_date_list))

        # 保存ディレクトリとファイル名の指定
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"racedate_{year}.txt")

        # ファイルに保存
        with open(save_path, "w", encoding="utf-8") as f:
            for race_date in race_date_list:
                f.write(str(race_date) + "\n")


if __name__ == "__main__":
    main()