import os
import time
from tqdm import tqdm

from data_scraping_module import get_race_and_horse_info
import pandas as pd

def main():

    year_list = [
        # 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
        # 2020, 2021, 2022, 2023
        2024
    ] 

    # race_idを取得
    for year in year_list:

        race_id_path = f"data/race_id/raceid_{year}.txt"
        if not os.path.exists(race_id_path):
            print(f"{race_id_path} が存在しません。スキップします。")
            continue

        with open(race_id_path, "r") as f:
            race_ids = [line.strip() for line in f if line.strip()]

        race_dfs = []
        horse_dfs = []

        race_info_path = f"data/race_info/race_info_{year}.csv"
        horse_info_path = f"data/race_info/race_horse_{year}.csv"
        race_info_written = os.path.exists(race_info_path)
        horse_info_written = os.path.exists(horse_info_path)

        for idx, race_id in enumerate(tqdm(race_ids, desc=f"Year {year}")):
            try:
                race_df, horse_df = get_race_and_horse_info(race_id)
                if race_df is not None:
                    race_dfs.append(race_df)
                if horse_df is not None:
                    horse_dfs.append(horse_df)
            except Exception as e:
                print(f"Error processing race_id {race_id}: {e}")

            time.sleep(1)  # サーバー負荷軽減のため

            # 100レースごとに保存
            if (idx + 1) % 100 == 0:
                if race_dfs:
                    race_info_df = pd.concat(race_dfs, ignore_index=True)
                    race_info_df.to_csv(
                        race_info_path,
                        mode="a" if race_info_written else "w",
                        header=not race_info_written,
                        index=False
                    )
                    race_info_written = True
                    race_dfs = []
                    
                if horse_dfs:
                    horse_info_df = pd.concat(horse_dfs, ignore_index=True)
                    horse_info_df.to_csv(
                        horse_info_path,
                        mode="a" if horse_info_written else "w",
                        header=not horse_info_written,
                        index=False
                    )
                    horse_info_written = True
                    horse_dfs = []

        # 残りを保存
        if race_dfs:
            race_info_df = pd.concat(race_dfs, ignore_index=True)
            race_info_df.to_csv(
                race_info_path,
                mode="a" if race_info_written else "w",
                header=not race_info_written,
                index=False
            )
        if horse_dfs:
            horse_info_df = pd.concat(horse_dfs, ignore_index=True)
            horse_info_df.to_csv(
                horse_info_path,
                mode="a" if horse_info_written else "w",
                header=not horse_info_written,
                index=False
            )

if __name__ == "__main__":
    main()




