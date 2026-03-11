import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

BASE_URL = "https://youdrivemecrazy.in/collection/page/{}/"
car_data = []

def extract_car_info(card):
    # Title and link
    title_item = card.find('a', class_='rmv_txt_drctn')
    title = title_item.text.strip() if title_item else None
    link = title_item['href'] if title_item else None

    # Image
    image_item = card.find('div', class_='thumb')
    image = image_item.find('img')['src'] if image_item and image_item.find('img') else None

    # Price
    price_span = card.find('span', class_='heading-font')
    price = price_span.text.strip() if price_span else None

    # Info (labels)
    info_item = card.find('div', class_='labels')
    info = info_item.text.strip() if info_item else None

    # Details (meta-middle units: name + value)
    detail_elems = card.find_all('div', class_='meta-middle-unit')
    details_dict = {}
    for unit in detail_elems:
        name_div = unit.find('div', class_='name')
        value_div = unit.find('div', class_='value')
        if name_div and value_div:
            key = name_div.text.strip()
            val = value_div.text.strip()
            details_dict[key] = val

    return {
        'Title': title,
        'Link': link,
        'Price': price,
        'Information': info,
        'Image': image,
        **details_dict   # expand structured details into separate columns
    }

for i in range(2,9):  # scrape pages 1–2 as an example
    print(f"Scraping page {i}")
    url = BASE_URL.format(i)
    response = requests.get(url, headers=HEADERS)
    print(response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Flexible selector: works for both list and grid layouts
    listings = soup.find_all('div', class_=['listing-list-loop', 'stm-directory-grid-loop'])
    if not listings:
        print('No Data Found')
    for card in listings:
        info = extract_car_info(card)
        if info:
            car_data.append(info)

    time.sleep(2)

# Save to CSV
df = pd.DataFrame(car_data)
print(df.head())

path = os.path.join(os.getcwd(), 'data', 'raw_data', 'you_drive_me_crazy_listings_delhi.csv')
os.makedirs(os.path.dirname(path), exist_ok=True)
df.to_csv(path, index=False)