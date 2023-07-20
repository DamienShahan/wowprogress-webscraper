import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd

pagenumber = -1
url = f'https://www.wowprogress.com/pve/rating/next/{pagenumber}/?lang=de'
print(url)

# returns a CloudScraper instance
scraper = cloudscraper.create_scraper()  

# Get wowproress data
wowprogress_raw = scraper.get(url)

# Parse wowprogress data
soup = BeautifulSoup(wowprogress_raw.text, 'html.parser')

# Find the main table
table = soup.find('table', {'class': 'rating'})
# Cast BeautifulSoup.Tag type to string
html = str(table)

# Output html to file
with open('wowprog.html', 'w', encoding="utf-8") as f:
    f.write(html)