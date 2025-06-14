import os
import pandas as pd
from data_scraping_module import get_race_and_horse_info

def main():
    year = 2024
    race_id_list = [
        "202401020804"
        # "202402010903", "202403010306", "202401010104",
        # "202403030112", "202404010806", "202401010604",
        # "202404040404", "202406010301", "202406020308",
        # "202406050102", "202406050504", "202406020709",
        # "202406050212", "202405010103", "202406020811",
        # "202406010408"
    ]

    for race_id in race_id_list:
        race_info_path = f"data/race_info/race_info_{year}.csv"
        horse_info_path = f"data/race_info/race_horse_{year}.csv"

        # 既存データの読み込み（race_idをstr型で読み込む）
        if os.path.exists(race_info_path):
            race_df = pd.read_csv(race_info_path, dtype={"race_id": str})
        else:
            race_df = pd.DataFrame()

        if os.path.exists(horse_info_path):
            horse_df = pd.read_csv(horse_info_path, dtype={"race_id": str})
        else:
            horse_df = pd.DataFrame()

        # 新しいデータの取得
        new_race_df, new_horse_df = get_race_and_horse_info(race_id)
        print(new_race_df)

        print(new_horse_df)

        # race_id列が存在する前提で処理
        if new_race_df is not None and not new_race_df.empty:
            new_race_df["race_id"] = new_race_df["race_id"].astype(str)
            race_df = race_df[race_df['race_id'] != str(race_id)]
            # race_dfの列を新しいrace_dfの列で置き換える
            race_df = pd.concat([race_df, new_race_df], ignore_index=True)
            race_df = race_df[new_race_df.columns]  # 列順・列名を新しいものに合わせる
            race_df = race_df.sort_values("race_id").reset_index(drop=True)  # race_idでソート
            race_df.to_csv(race_info_path, index=False)

        if new_horse_df is not None and not new_horse_df.empty:
            new_horse_df["race_id"] = new_horse_df["race_id"].astype(str)
            horse_df = horse_df[horse_df['race_id'] != str(race_id)]
            horse_df = pd.concat([horse_df, new_horse_df], ignore_index=True)
            horse_df = horse_df.sort_values("race_id").reset_index(drop=True)  # race_idでソート
            horse_df.to_csv(horse_info_path, index=False)

        print(f"Updated race_id {race_id} for year {year}.")

if __name__ == "__main__":
    main()