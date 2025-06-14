import os
import time
from tqdm import tqdm

from data_scraping_module import get_raceid_list

def main():
    race_date_dir = "data/race_date"
    race_id_dir = "data/race_id"
    year_list = [
        # 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 
        2020, 2021, 2022, 2023, 2024
    ]  # 保存する年のリスト


    for year in year_list:

        date_file = os.path.join(race_date_dir, f"racedate_{year}.txt")
        if not os.path.exists(date_file):
            print(f"File not found: {date_file}")
            continue

        with open(date_file, "r", encoding="utf-8") as f:
            race_dates = [line.strip() for line in f if line.strip()]

        race_id_list = []
        for race_date in tqdm(race_dates, desc=f"Year {year}"):
            ids = get_raceid_list(race_date)
            race_id_list.extend(ids)
            time.sleep(1)  # サーバー負荷軽減

        # 重複を除去してソート
        race_id_list = sorted(set(race_id_list))

        # 保存ディレクトリとファイル名の指定
        os.makedirs(race_id_dir, exist_ok=True)
        save_path = os.path.join(race_id_dir, f"raceid_{year}.txt")

        # ファイルに保存
        with open(save_path, "w", encoding="utf-8") as f:
            for race_id in race_id_list:
                f.write(str(race_id) + "\n")

if __name__ == "__main__":
    main()