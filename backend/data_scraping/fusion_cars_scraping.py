import requests
from bs4 import BeautifulSoup
import csv

headers = {"User-Agent": "Mozilla/5.0"}
base_url = "https://fusioncars.in/collections/"
response = requests.get(base_url, headers=headers)

print("Main page status:", response.status_code)
print("Main page URL:", response.url)

soup = BeautifulSoup(response.text, "html.parser")

# Collect all car detail page links
car_links = [a['href'] for a in soup.find_all("a", href=True) if "/cars/" in a['href']]
print("Found", len(car_links), "car links")

car_data = []

for idx, link in enumerate(car_links, start=1):
    car_page = requests.get(link, headers=headers)
    print(f"\n[{idx}/{len(car_links)}] Scraping:", link, "Status:", car_page.status_code)

    car_soup = BeautifulSoup(car_page.text, "html.parser")

    # Title
    title_tag = car_soup.find("h5")
    title = title_tag.get_text(strip=True) if title_tag else None
    print(" → Title:", title)

    # Details (Registered, Fuel, Kms)
    details = {}
    info_section = car_soup.find("div", class_="car_info")
    if info_section:
        items = info_section.find_all("li")
        for item in items:
            key = item.find("h6").get_text(strip=True)
            value = item.find("span", class_="asert").get_text(strip=True)
            details[key] = value

    # Price
    price_tag = car_soup.find("div", class_="car-price")
    price = price_tag.get_text(strip=True) if price_tag else None
    print(" → Price:", price)

    # Image URL
    img_tag = car_soup.find("img")
    img_url = img_tag['src'] if img_tag else None

    # Sold badge
    sold_tag = car_soup.find("div", class_="my-badge")
    sold_status = sold_tag.get_text(strip=True) if sold_tag else "Available"
    print(" → Status:", sold_status)

    car_data.append({
        "Title": title,
        "Registered": details.get("Registered"),
        "Fuel": details.get("Fuel"),
        "Kms": details.get("Kms"),
        "Price": price,
        "Image_URL": img_url,
        "Sold_Status": sold_status,
        "URL": link
    })

# Save to CSV
with open("fusioncars_data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Title", "Registered", "Fuel", "Kms", "Price", "Image_URL", "Sold_Status", "URL"])
    writer.writeheader()
    writer.writerows(car_data)

print("\nData saved to fusioncars_data.csv")