import re
import time
import datetime

import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_racedate_list(year: int, month: int) -> list[str]:
    """
    指定した年・月のnetkeibaカレンダーから開催日IDリストを取得する

    Args:
        year (int): 年（例: 2025）
        month (int): 月（例: 5）

    Returns:
        list[str]: 開催日IDのリスト（例: ["20250503", ...]）
    """
    url = f"https://race.netkeiba.com/top/calendar.html?year={year}&month={month}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", class_="Calendar_Table")
    if not table:
        return []
    links = table.find_all("a")
    racedate_list = []
    for link in links:
        href = link.get("href")
        m = re.search(r"\d+$", href)
        if m:
            racedate_list.append(m.group())
    return racedate_list

def get_raceid_list(racedate: str) -> list[str]:
    """
    指定した開催日ID（yyyymmdd）から、その日の全レースID一覧を取得する

    Args:
        racedate (str): 開催日ID（例: "20250503"）

    Returns:
        list[str]: レースIDのリスト（例: ["202505031101", ...]）
    """
    url = f"https://db.netkeiba.com/race/list/{racedate}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")
    raceid_list = []
    # レース情報が含まれる <dl class="race_top_data_info fc"> を全て取得
    race_dl_list = soup.body.find_all("dl", class_="race_top_data_info fc")
    for dl in race_dl_list:
        a_tag = dl.find('a')
        if a_tag and a_tag.get('href'):
            m = re.search(r'/race/(\d{12})/', a_tag['href'])
            if m:
                raceid_list.append(m.group(1))
    return raceid_list

def get_race_and_horse_info(race_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    指定したレースIDからレース情報（race_df）と出走馬情報（horse_df）を取得する

    Args:
        race_id (str): レースID（例: "202505021211"）

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (race_df, horse_df)
    """


    url = f"https://db.netkeiba.com/race/{race_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    r.encoding = 'euc_jp' 
    html = r.text
    soup = BeautifulSoup(html, "html.parser")

    # --- レース情報 DataFrame を作成 ---
    # race_id
    m = re.search(r"/race/(\d{12})/|get_race_result_horse_laptime\('(\d{12})'", html)
    race_id_extracted = next(g for g in m.groups() if g) if m else race_id

    # 開催日・開催回次・レースタイプ
    smalltxt = soup.select_one("p.smalltxt").get_text(" ", strip=True)
    date_ja, meeting_round, race_type, *_ = smalltxt.split()
    y, mth, d = map(int, re.findall(r"\d+", date_ja))
    race_date = datetime.date(y, mth, d).isoformat()

    # レース番号
    race_number = soup.select_one("dl.racedata dt").get_text(strip=True).replace("R", "").strip()

    # レース名・クラス
    title_full = soup.select_one("dl.racedata h1").get_text(strip=True)
    m_class = re.search(r"\(([^)]+)\)", title_full)
    race_class = m_class.group(1) if m_class else ""
    race_name  = re.sub(r"\([^)]*\)", "", title_full).strip()

    # 開催競馬場の場所（例：東京）
    m_loc = re.search(r"\d+回([^0-9]+?)\d+日", meeting_round)
    racecourse_location = m_loc.group(1) if m_loc else ""

    # コース情報
    span_txt = soup.select_one("dl.racedata span").get_text(" ", strip=True)
    course_segment = span_txt.split("/")[0].strip()

    # コース表記の正規表現を改良（ダート・芝両対応、表記ゆれ対応）
    cm = re.search(r"(芝|ダ|ダート)(左|右|直線)?\s*(\d+)m", course_segment)
    if cm:
        # 「ダ」は「ダート」に統一
        surface = cm.group(1)
        course_surface = "ダート" if surface in ["ダ", "ダート"] else "芝"
        course_direction = cm.group(2) if cm.group(2) else ""
        race_distance = int(cm.group(3))
    else:
        course_surface = ""
        course_direction = ""
        race_distance = 0

    # 天候・馬場状態（芝・ダート両対応）
    m_weather = re.search(r"天候\s*:\s*([^\s/]+)", span_txt)
    weather = m_weather.group(1) if m_weather else ""
    m_track = re.search(r"(芝|ダート)\s*:\s*([^\s/]+)", span_txt)
    track_condition = m_track.group(2) if m_track else ""

    # 頭数（出走馬数）
    race_table = soup.find("table", class_="race_table_01")
    entry_count = len(race_table.find_all("tr")) - 1 if race_table else 0

    race_info = {
        "race_id"               : race_id,
        "race_date"             : race_date,
        "meeting_round"         : meeting_round,
        "race_type"             : race_type,
        "race_number"           : race_number,
        "race_name"             : race_name,
        "race_class"            : race_class,
        "racecourse_location"   : racecourse_location,
        "course_surface"        : course_surface,
        "course_direction"      : course_direction,
        "race_distance"         : race_distance,
        "weather"               : weather,
        "track_condition"       : track_condition,
        "entry_count"           : entry_count, 
    }
    race_df = pd.DataFrame([race_info])

    # --- 出走馬情報 DataFrame を作成 ---
    body_rows = race_table.find_all("tr")[1:] if race_table else []
    horse_records: list[dict] = []
    for tr in body_rows:
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        cells.extend([""] * (21 - len(cells)))
        age_match = re.search(r"\d+", cells[4])
        age = age_match.group() if age_match else ""
        sex = cells[4].replace(age, "")
        link = tr.find("a", href=re.compile(r"^/horse/\d+/"))
        horse_id_ = ""
        if link:
            m = re.search(r"/horse/(\d+)/", link["href"])
            if m:
                horse_id_ = m.group(1)
        rec = {
            "race_id"        : race_id_extracted,
            "finish_position": cells[0],
            "frame_number"   : cells[1],
            "horse_number"   : cells[2],
            "horse_name"     : cells[3],
            "horse_id"       : horse_id_,
            "sex"            : sex,
            "age"            : age,
            "weight_carried" : cells[5],
            "jockey"         : cells[6],
            "race_time"      : cells[7],
            "margin"         : cells[8],
            "last_3f"        : cells[11],
            "odds"           : cells[12],
            "popularity"     : cells[13],
            "body_weight"    : cells[14],
            "trainer"        : cells[18],
            "owner"          : cells[19],
            "prize_money"    : cells[20],
        }
        horse_records.append(rec)
    horse_df = pd.DataFrame(horse_records, columns=[
        "race_id", "finish_position", "frame_number", "horse_number", "horse_name", "horse_id", 
        "sex", "age", "weight_carried", "jockey", "race_time", "margin",
        "last_3f", "odds", "popularity", "body_weight", "trainer", "owner", "prize_money",
    ])
    return race_df, horse_df