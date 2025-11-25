# services/price_service.py

import requests
from bs4 import BeautifulSoup
import copy
import threading
import time
import logging

from utils.formatter import get_turkish_datetime_str

URL = "https://finans.mynet.com/altin/"
UPDATE_INTERVAL_SECONDS = 60 
CACHED_PRICES = {} 
LAST_UPDATE_TIME = "" 

GOLD_OPTIONS = {
    'Gram Altın': 'Gram Altın',
    'Ons Altın (USD)': 'Ons Altın / USD',
    'Ons Altın (TL)': 'Ons Altın / TL',
    'Çeyrek Altın': 'Çeyrek Altın',
    'Yarım Altın': 'Yarım Altın',
    'Cumhuriyet Altını': 'Cumhuriyet Altını',
    'Ata Altın': 'Ata Altın'
}

logger = logging.getLogger(__name__)

def fetch_all_prices():
    global CACHED_PRICES, LAST_UPDATE_TIME
    new_prices = {}
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        for display_name, gold_type_title in GOLD_OPTIONS.items():
            gold_link_element = soup.find('a', title=gold_type_title)
            if gold_link_element:
                gold_row = gold_link_element.find_parent('tr')
                if gold_row:
                    all_columns = gold_row.find_all('td')
                    if len(all_columns) > 4:
                        buy_price = all_columns[3].text.strip()
                        new_prices[gold_type_title] = buy_price
                        continue
            new_prices[gold_type_title] = CACHED_PRICES.get(gold_type_title, "Bilgi alınamadı")
            
        CACHED_PRICES = copy.deepcopy(new_prices) 
        LAST_UPDATE_TIME = get_turkish_datetime_str()
        logger.info(f"Cache successfully updated. Time: {LAST_UPDATE_TIME}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Web request error (General): {e}")
    except Exception as e:
        logger.error(f"Unexpected error occurred (General): {e}")

def get_cached_prices():
    return CACHED_PRICES, LAST_UPDATE_TIME, GOLD_OPTIONS

def start_background_updater():
    fetch_all_prices()
    def run_update():
        while True:
            time.sleep(UPDATE_INTERVAL_SECONDS)
            fetch_all_prices()
    thread = threading.Thread(target=run_update, daemon=True)
    thread.start()
    logger.info(f"Price update thread started, running every {UPDATE_INTERVAL_SECONDS} seconds.")