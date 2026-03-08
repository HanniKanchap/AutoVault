import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

brands = [
    "maruti", "hyundai", "honda", "toyota", "tata",
    "mahindra", "kia", "ford", "volkswagen", "audi",
    "bmw", "nissan", "mercedes-benz"
]

BASE_URL = "https://www.cardekho.com/used-{brand}-cars+in+delhi-ncr/page-{page}"

car_data = []

def clean_price(price_str):
    try:
        price_str = price_str.replace('₹', '').replace(',', '').strip()
        if 'Lakh' in price_str:
            price = float(price_str.replace('Lakh','').strip()) * 100000
            return f"₹ {price:,.0f}"
        elif 'Crore' in price_str:
            price = float(price_str.replace('Crore','').strip()) * 10000000
            return f"₹ {price:,.0f}"
        else:
            return f"₹ {price_str}"
    except:
        return price_str

def extract_car_info_cardekho(card):
    try:
        title_elem = card.find('h3')
        title = title_elem.text.strip() if title_elem else 'N/A'

        price_elem = card.find('div', class_='priceAssured')
        if price_elem:
            p_tag = price_elem.find('p')
            price = clean_price(p_tag.text.strip()) if price_elem else 'N/A'

        link_elem = card.find('a', href=True)
        link = 'https://www.cardekho.com' + link_elem['href'] if link_elem else 'N/A'

        img_elem = card.find('img',class_='hover')
        image = img_elem['src'] if img_elem and 'src' in img_elem.attrs else 'N/A'

        specs = card.find_all('div', class_='dotsDetails')
        spec_list = [s.text.strip() for s in specs]
        info_text = ' | '.join(spec_list) if spec_list else 'N/A'

        location_elem = card.find('div',class_='distanceText')
        location = location_elem.text.strip() if location_elem else 'N/A'

        return {
            'Title': title,
            'Link': link,
            'Price': price,
            'Information': info_text,
            'Image': image,
            'Year': title.split()[0] if title != 'N/A' else 'N/A',
            'Brand':title.split()[1] if title != 'N/A' else 'N/A',
            'Location':location
        }
    except Exception as e:
        print(f"Error extracting car info: {e}")
        return None

def scrape_cardekho(brand, max_pages=20):
    print(f"\nScraping CarDekho for {brand.upper()}")
    for page in range(2, max_pages+1):
        url = BASE_URL.format(brand=brand, page=page)
        print(f"Fetching {url}")
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                listings = soup.find_all('div', class_='NewUcExCard posR')
                if not listings:
                    print(f"No more cars found for {brand} at page {page}.")
                    break
                for card in listings:
                    car_info = extract_car_info_cardekho(card)
                    if car_info:
                        car_data.append(car_info)
                        print(f"✓ {car_info['Title']} - {car_info['Price']}")
            else:
                print("Request failed.")
                break
        except Exception as e:
            print(f"Error: {e}")
            break
    

print("Starting CarDekho Delhi Scraper")
for brand in brands:
    scrape_cardekho(brand, max_pages=30)

if car_data:
    df = pd.DataFrame(car_data)
    os.makedirs(os.path.join(os.getcwd(), 'data', 'raw_data'), exist_ok=True)
    path = os.path.join(os.getcwd(), 'data', 'raw_data', 'cardekho_listings_delhi.csv')
    df.to_csv(path, index=False)
    print(f"\n✓ Data saved to: {path}")
else:
    print("\n⚠ No data scraped! The website structure may have changed.")