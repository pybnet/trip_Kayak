import json
import time
import os
import requests
from urllib.parse import urlencode
from lxml import html
from dotenv import load_dotenv

load_dotenv()

cities = json.load(open('cities.json'))
SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")


def scrape_city(city):
    params = {'ss': city, 'lang': 'fr', 'rows': '5'}
    booking_url = f"https://www.booking.com/searchresults.html?{urlencode(params)}"
    scraper_url = "http://api.scraperapi.com?" + urlencode({
        'api_key': SCRAPERAPI_KEY,
        'url': booking_url,
        'render': 'true',
        'premium': 'true',
        'country_code': 'fr',
    })

    response = requests.get(scraper_url, timeout=120)
    if response.status_code != 200:
        print(f"  [{city}] ERROR {response.status_code} — skipping")
        return []

    hotels = html.fromstring(response.text).xpath('//div[@data-testid="property-card"]')[:5]
    print(f"  [{city}] Found {len(hotels)} hotels")

    city_results = []
    for hotel in hotels:
        city_results.append({
            'ville': city,
            'nom': "".join(hotel.xpath('.//*[@data-testid="title"]//text()')).strip(),
            'url': "".join(hotel.xpath('.//*[@data-testid="title-link"]/@href')),
            'note': "".join(hotel.xpath('.//*[@data-testid="review-score"]//text()')).strip() or None,
            'adresse': "".join(hotel.xpath('.//*[@data-testid="address-link"]//text()')).strip() or None,
            'distance': "".join(hotel.xpath('.//*[@data-testid="distance"]//text()')).strip() or None,
        })
    return city_results


results = []
print(f"Scraping {len(cities)} cities sequentially...\n")

for city in cities:
    results.extend(scrape_city(city))
    time.sleep(5)

with open("hotels.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nDone. {len(results)} hotels saved to hotels.json")