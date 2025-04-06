import os
os.environ['CHROME_BINARY'] = "/content/chrome-linux64/chrome"
os.environ['PATH'] += os.pathsep + "/content/chromedriver-linux64"

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import csv

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = os.environ["CHROME_BINARY"]

driver = webdriver.Chrome(service=Service("/content/chromedriver-linux64/chromedriver"), options=chrome_options)
print("Going to https://ow.blizzard.cn/herolist/#/")
driver.get("https://ow.blizzard.cn/herolist/#/") 
time.sleep(5)

name_dictionary = {
    "安娜": "Ana",
    "雾子": "Kiriko",
    "源氏": "Genji",
    "莫伊拉": "Moira",
    "索杰恩": "Sojourn",
    "士兵：76": "Soldier: 76",
    "卡西迪": "Cassidy",
    "禅雅塔": "Zenyatta",
    "死神": "Reaper",
    "朱诺": "Juno",
    "艾什": "Ashe",
    "拉玛刹": "Ramattra",
    "天使": "Mercy",
    "查莉娅": "Zarya",
    "堡垒": "Bastion",
    "卢西奥": "Lúcio",
    "毛加": "Mauga",
    "半藏": "Hanzo",
    "法老之鹰": "Pharah",
    "伊拉锐": "Illari",
    "末日铁拳": "Doomfist",
    "探奇": "Venture",
    "狂鼠": "Junkrat",
    "西格玛": "Sigma",
    "布丽吉塔": "Brigitte",
    "黑百合": "Widowmaker",
    "生命之梭": "Lifeweaver",
    "黑影": "Sombra",
    "D.VA": "D.VA",
    "托比昂": "Torbjörn",
    "猎空": "Tracer",
    "奥丽莎": "Orisa",
    "骇灾": "Hazard",
    "温斯顿": "Winston",
    "莱因哈特": "Reinhardt",
    "渣客女王": "Junker Queen",
    "巴蒂斯特": "Baptiste",
    "美": "Mei",
    "路霸": "Roadhog",
    "回声": "Echo",
    "秩序之光": "Symmetra",
    "破坏球": "Wrecking Ball"
}

data_dict = {}

def parse_table(is_control_variant=False):
    try:
        # Re-locate the table body each time before interaction to avoid StaleElementReferenceException
        table_body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "el-table__body-wrapper"))
        )

        rows = table_body.find_elements(By.CLASS_NAME, "el-table__row")
        if not rows:
            print("No rows found in table.")
            return

        for row in rows:
            try:
                cols = []
                for i in range(1, 5):
                    col = row.find_element(By.CLASS_NAME, f"el-table_1_column_{i}")
                    if i == 1:
                        name_elem = col.find_element(By.CLASS_NAME, "name")
                        name = name_elem.text.strip()
                        if is_control_variant:
                            name += "C"
                        if name not in data_dict:
                            data_dict[name] = []
                    else:
                        span = col.find_element(By.TAG_NAME, "span")
                        data_dict[name].append(span.text.strip())
            except Exception as row_err:
                print(f"Error parsing row: {row_err}")
    except TimeoutException:
        print("Table body not found (timeout).")

def cycle_dropdown(is_first_loop=False):
    if is_first_loop:
        print(f"Switched to dropdown: 全部段位")
        parse_table(is_control_variant=not is_first_loop)  # collect the first table BEFORE cycling

    # Re-locate the dropdown elements each time to avoid StaleElementReferenceException
    sel_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "select-box"))
    )
    sel_items = sel_box.find_elements(By.CLASS_NAME, "sel-item")
    rank_sel = sel_items[2]

    # I don't know what this does anymore, but if removed, everything breaks
    if not is_first_loop:
        try:
            sel_show = WebDriverWait(rank_sel, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "sel-show"))
            )
            sel_show.click()
            time.sleep(1)

            sel_list = WebDriverWait(rank_sel, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sel-list"))
            )
            sel_inner = sel_list.find_element(By.CLASS_NAME, "sel-inner")
            rank_options = sel_inner.find_elements(By.TAG_NAME, "a")

            if rank_options:
                driver.execute_script("arguments[0].click();", rank_options[0])
                print(f"Reset dropdown to: {rank_options[0].text.strip()}")
                time.sleep(4)
                parse_table(is_control_variant=True)
        except Exception as e:
            print(f"Error resetting dropdown.")

    for _ in range(9):
        try:
            # Re-locate dropdown elements for each iteration to avoid StaleElementReferenceException
            sel_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "select-box"))
            )
            sel_items = sel_box.find_elements(By.CLASS_NAME, "sel-item")
            rank_sel = sel_items[2]

            sel_show = WebDriverWait(rank_sel, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "sel-show"))
            )
            sel_show.click()
            time.sleep(1)

            # Re-locate the dropdown list and options to avoid stale elements
            sel_list = WebDriverWait(rank_sel, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sel-list"))
            )
            sel_inner = sel_list.find_element(By.CLASS_NAME, "sel-inner")
            rank_options = sel_inner.find_elements(By.TAG_NAME, "a")

            current_index = -1
            for idx, opt in enumerate(rank_options):
                if "on" in opt.get_attribute("class"):
                    current_index = idx
                    break

            # Reset the dropdown to the first item at the end
            if current_index == -1 or current_index + 1 >= len(rank_options):
                print("Reached last dropdown item.")
                first_option = rank_options[0]
                key = first_option.text.strip()
                driver.execute_script("arguments[0].click();", first_option)
                break

            # Account for Selenium's nonsense
            if current_index == 0 and not is_first_loop:
                print(f"Switched to dropdown: 全部段位")
                parse_table(is_control_variant=not is_first_loop)

            next_option = rank_options[current_index + 1]
            key = next_option.text.strip()
            driver.execute_script("arguments[0].click();", next_option)
            print(f"Switched to dropdown: {key}")
            time.sleep(4)
            parse_table(is_control_variant=not is_first_loop)

        except Exception as e:
            print(f"cycle_dropdown failed")
            break

def rename_keys_with_dictionary(data_dict, name_dictionary):
    renamed_dict = {}
    for key, value in data_dict.items():
        is_control_variant = key.endswith("C")
        base_name = key[:-1] if is_control_variant else key

        english_name = name_dictionary.get(base_name, base_name)

        # Re-append "C" if it was competitive data (why'd I call that control?)
        final_name = english_name + "C" if is_control_variant else english_name

        renamed_dict[final_name] = value
    return renamed_dict

# Phase 1: Quick play data
cycle_dropdown(is_first_loop=True)

# Phase 2: Switch over to competitive data
buttons = driver.find_elements(By.CLASS_NAME, "btn")
for btn in buttons:
    if "on" not in btn.get_attribute("class"):
        btn.click()
        time.sleep(6)
        break

# Phase 3: Collect competitive data
cycle_dropdown(is_first_loop=False)

# Translate hero names
data_dict = rename_keys_with_dictionary(data_dict, name_dictionary)

# Export everything to a CSV
today = os.environ.get("TODAY", "unknown_date") # (incl. fallback value)
filename = f"data/{today}_hero_data.csv"
max_len = max(len(v) for v in data_dict.values())

header = ["Hero",
          "All", "", "",
          "Bronze", "", "",
          "Silver", "", "",
          "Gold", "", "",
          "Platinum", "", "",
          "Diamond", "", "",
          "Master", "", "",
          "Grandmaster", "", "",
          "Champion"]

with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for key, values in data_dict.items():
        writer.writerow([key] + values + [""] * (len(header) - 1 - len(values)))

print(f"Data exported to {filename}")
driver.quit()