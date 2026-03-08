import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

brand_models = {
    "maruti": [
        "wagon-r", "alto", "swift", "dzire", "baleno",
        "ertiga", "brezza", "celerio", "ignis", "ciaz",
        "s-cross", "xl6", "fronx", "grand-vitara", "esteem"
    ],
    "hyundai": [
        "i10", "i20", "creta", "venue", "verna",
        "grand-i10", "santro", "aura", "alcazar", "tucson",
        "kona", "elantra", "accent", "getz", "sonata"
    ],
    "honda": [
        "city", "amaze", "jazz", "wr-v", "br-v",
        "brio", "civic", "accord", "cr-v", "mobilio",
        "pilot", "legend", "nsx", "odyssey", "hr-v"
    ],
    "toyota": [
        "innova", "fortuner", "glanza", "urban-cruiser", "corolla",
        "etios", "yaris", "camry", "land-cruiser", "hilux",
        "prius", "rav4", "avanza", "celica", "supra"
    ],
    "tata": [
        "nexon", "altroz", "harrier", "safari", "tiago",
        "tigor", "punch", "zest", "bolt", "indica",
        "indigo", "sumo", "hex", "aria", "venture"
    ],
    "mahindra": [
        "scorpio", "xuv500", "xuv700", "thar", "bolero",
        "marazzo", "kuv100", "tuv300", "alturas", "verito"
    ],
    "mercedes-benz": [
        "c-class", "e-class", "s-class", "glc", "gle",
        "gls", "a-class", "gla", "cla", "g-class"
    ],
    "ford": [
        "ecosport", "figo", "aspire", "endeavour", "freestyle",
        "fiesta", "ikon", "fusion", "mondeo", "mustang"
    ],
    "volkswagen": [
        "polo", "vento", "taigun", "tiguan", "passat",
        "beetle", "jetta", "touareg", "ameo", "cross-polo"
    ],
    "audi": [
        "a3", "a4", "a6", "q3", "q5",
        "q7", "q8", "tt", "rs5", "s5"
    ],
    "nissan": [
        "magnite", "kicks", "sunny", "micra", "terrano",
        "x-trail", "evalia", "teana", "370z", "gt-r"
    ],
    "bmw": [
        "3-series", "5-series", "7-series", "x1", "x3",
        "x5", "x7", "z4", "m3", "m5"
    ],
    "kia": [
        "seltos", "sonet", "carnival", "carens", "sportage",
        "sorento", "stinger", "rio", "ceed", "ev6"
    ]
}

BASE_URL = ("https://www.cars24.com/buy-used-{}-{}-cars-delhi-ncr/"
            "?sort=bestmatch&serveWarrantyCount=true&listingSource=TabFilter&storeCityId=1")

car_data = []

def clean_price(price_str):
    try:
        price_str = price_str.replace('₹', '').replace(',', '').strip()
        if 'Cr' in price_str:
            price_str = price_str.replace('Cr', '').strip()
            price = float(price_str) * 10000000
            return f"₹ {price:,.0f}"
        elif 'L' in price_str:
            price_str = price_str.replace('L', '').strip()
            price = float(price_str) * 100000
            return f"₹ {price:,.0f}"
        else:
            return f"₹ {price_str}"
    except:
        return price_str

def extract_car_info_cars24(card):
    try:
        # Title
        title_elem = card.find('span', class_='sc-bcXHqh bAcffq')
        title = title_elem.text.strip() if title_elem else 'N/A'

        # Price
        del_price_elem = card.find('p', class_='sc-bcXHqh hnqWZb')
        del_price = clean_price(del_price_elem.text.strip()) if del_price_elem else 'N/A'

        price_elem = card.find('p', class_='sc-bcXHqh hvRpEM')
        price = clean_price(price_elem.text.strip()) if price_elem else 'N/A'

        # Link
        link = card['href'] if card.has_attr('href') else 'N/A'

        # Image
        img_elem = card.find('img', class_='shrinkOnTouch')
        image = img_elem['src'] if img_elem and 'src' in img_elem.attrs else 'N/A'

        # Specs (year, km, fuel, transmission, etc.)
        specs = card.find_all('p', class_='sc-bcXHqh kNDBvu')
        spec_list = [s.text.strip() for s in specs]
        info_text = ' | '.join(spec_list) if spec_list else 'N/A'

        # Location
        location_item = card.find('p', class_='sc-bcXHqh bKVBht')
        location = location_item.text.strip() if location_item else 'N/A'

        # Brand
        Year = title.split()[0] if title != 'N/A' else 'N/A'
        brand = title.split()[1] if title != 'N/A' else 'N/A'

        return {
            'Title': title,
            'Link': link,
            'Price': price,
            'Del Price':del_price,
            'Information': info_text,
            'Image': image,
            'Year': Year,
            'Brand':brand,
            'Location':location
        }
    except Exception as e:
        print(f"Error extracting car info: {e}")
        return None

def scrape_cars24(brand,model):
    print(f"\nScraping Cars24 for {brand.upper()} {model.upper()}")
    url = BASE_URL.format(brand,model)
    print(f"URL: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=100)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = soup.find_all('a', {'class': 'styles_carCardWrapper__sXLIp'})
            if not listings:
                print(f"No cars found for {brand}.")
                return
            for card in listings:
                car_info = extract_car_info_cars24(card)
                if car_info:
                    car_data.append(car_info)
                    print(f"✓ {car_info['Title']} - {car_info['Price']}")
        else:
            print("Request failed.")
    except Exception as e:
        print(f"Error: {e}")

print("Starting Cars24 Delhi Scraper")
for brand,models in brand_models.items():
    for model in models:
        scrape_cars24(brand,model)

if car_data:
    df = pd.DataFrame(car_data)
    os.makedirs(os.path.join(os.getcwd(), 'data', 'raw_data'), exist_ok=True)
    path = os.path.join(os.getcwd(), 'data', 'raw_data', 'cars24_listings_delhi.csv')
    df.to_csv(path, index=False)
    print(f"\n✓ Data saved to: {path}")
else:
    print("\n⚠ No data scraped! The website structure may have changed.")