import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time  # Import the time module for sleep

# Create a CloudScraper instance
scraper = cloudscraper.create_scraper()

# Initialize lists to store guild data
ranks = []
guild_names = []
guild_realms = []
guild_links = []

# Initialize the pagenumber and rank limit
pagenumber = -1
max_rank = 2000
keep_scraping = True

# Start scraping until we hit rank 1000 or more
while keep_scraping:
    # Construct the URL for the current page
    url = f'https://www.wowprogress.com/pve/rating/next/{pagenumber}/?raids_week=1-2'
    print(f'Scraping page {pagenumber}...')

    # Get the webpage data
    wowprogress_raw = scraper.get(url)
    soup = BeautifulSoup(wowprogress_raw.text, 'html.parser')

    # Find the main table
    table = soup.find('table', {'class': 'rating'})

    # Loop through all rows in the table
    for row in table.find_all('tr')[1:]:  # Skip the header row
        rank_tag = row.find('span', class_='rank')
        guild_tag = row.find('a', class_='guild')
        realm_tag = row.find('a', class_='realm')

        if rank_tag and guild_tag and realm_tag:
            # Extract rank
            rank = int(rank_tag.text.strip())  # Convert rank to an integer
            
            # Stop scraping if the rank exceeds 1000
            if rank >= max_rank:
                keep_scraping = False
                break

            # Extract guild name
            guild_name = guild_tag.text.strip()

            # Extract guild realm
            guild_realm = realm_tag.text.strip()

            # Check if the realm does not start with "US-" or "EU (RU)-"
            if not guild_realm.startswith('US') and not guild_realm.startswith('EU (RU)') and not guild_realm.startswith('EU (FR)') and not guild_realm.startswith('OC'):
                # Extract guild link (href attribute)
                guild_link = f"https://www.wowprogress.com{guild_tag['href']}"

                # Append the extracted data to respective lists
                ranks.append(rank)
                guild_names.append(guild_name)
                guild_realms.append(guild_realm)
                guild_links.append(guild_link)
                
    # Wait for 1 second to avoid overloading the webserver
    time.sleep(1)

    # Increment the page number for the next loop
    pagenumber += 1

# Create a DataFrame from the extracted data
df = pd.DataFrame({
    'Rank': ranks,
    'Guild Name': guild_names,
    'Realm': guild_realms,
    'Link': guild_links
})

# Save the DataFrame to a CSV file
df.to_csv('wowprogress_guilds_with_ranks_filtered_to_2000.csv', index=False, encoding='utf-8')

print("CSV file 'wowprogress_guilds_with_ranks_filtered_to_2000.csv' created successfully!")
