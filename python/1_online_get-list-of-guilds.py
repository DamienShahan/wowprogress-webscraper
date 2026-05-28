import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import yaml
import os


def load_settings(path="settings.yaml"):
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def is_cloudflare_challenge(html: str) -> bool:
    cloudflare_indicators = [
        "Just a moment",
        "Checking if the site connection is secure",
        "Verify you are human",
        "cf-browser-verification",
        "cf-challenge",
        "challenge-platform",
        "cloudflare",
    ]

    html_lower = html.lower()
    return any(indicator.lower() in html_lower for indicator in cloudflare_indicators)


# User Settings
settings = load_settings()

max_rank = settings.get("max_rank", 500)
raids_week = settings.get("raids_week", "1-2")

# Create output folder if it does not exist
os.makedirs("output", exist_ok=True)

# Create a CloudScraper instance
scraper = cloudscraper.create_scraper()

# Initialize lists to store guild data
ranks = []
guild_names = []
guild_realms = []
guild_links = []

# Initialize variables for pagination
pagenumber = -1
keep_scraping = True

while keep_scraping:
    url = f"https://www.wowprogress.com/pve/rating/next/{pagenumber}/?raids_week={raids_week}"
    print(f"Url: {url}")
    print(f"Scraping page {pagenumber}")

    response = scraper.get(url)

    if response.status_code != 200:
        print(f"Failed to load page {pagenumber}. Status code: {response.status_code}")
        break

    if is_cloudflare_challenge(response.text):
        print("Cloudflare human verification page detected.")
        print("The scraper cannot continue because WowProgress requires browser-based human verification.")

        debug_file = f"output/cloudflare_page_{pagenumber}.html"
        with open(debug_file, "w", encoding="utf-8") as file:
            file.write(response.text)

        print(f"Saved received HTML to: {debug_file}")
        break

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", {"class": "rating"})

    if table is None:
        print(f"No rating table found on page {pagenumber}.")
        print("This may mean WowProgress changed its HTML, returned an error page, or blocked the request.")

        debug_file = f"output/debug_page_{pagenumber}.html"
        with open(debug_file, "w", encoding="utf-8") as file:
            file.write(response.text)

        print(f"Saved received HTML to: {debug_file}")
        break

    for row in table.find_all("tr")[1:]:
        rank_tag = row.find("span", class_="rank")
        guild_tag = row.find("a", class_="guild")
        realm_tag = row.find("a", class_="realm")

        if rank_tag and guild_tag and realm_tag:
            rank = int(rank_tag.text.strip())

            # Stop scraping once the rank is above the configured max rank.
            # This includes max_rank itself.
            if rank > max_rank:
                keep_scraping = False
                break

            guild_name = guild_tag.text.strip()
            guild_realm = realm_tag.text.strip()

            # Exclude unwanted regions
            if (
                not guild_realm.startswith("US")
                and not guild_realm.startswith("EU (RU)")
                and not guild_realm.startswith("EU (FR)")
                and not guild_realm.startswith("OC")
            ):
                guild_link = f"https://www.wowprogress.com{guild_tag['href']}"

                ranks.append(rank)
                guild_names.append(guild_name)
                guild_realms.append(guild_realm)
                guild_links.append(guild_link)

    time.sleep(1)
    pagenumber += 1


df = pd.DataFrame({
    "Rank": ranks,
    "Guild Name": guild_names,
    "Realm": guild_realms,
    "Link": guild_links,
})

output_path = "output/wowprogress_guild_list.csv"
df.to_csv(output_path, index=False, encoding="utf-8")

print(f"CSV file '{output_path}' created successfully!")