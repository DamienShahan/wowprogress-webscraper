import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time  # Import the time module for sleep

# Create a CloudScraper instance
scraper = cloudscraper.create_scraper()

# Read the existing CSV file
input_csv = 'wowprogress_guilds_with_ranks_filtered_to_2000.csv'
df = pd.read_csv(input_csv)

# Initialize an empty list to store the raids_week values
raids_week_values = []

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    guild_link = row['Link']
    
    print(f"Fetching data for {row['Guild Name']}...")

    # Fetch the guild's page using the link
    guild_page_raw = scraper.get(guild_link)
    
    # Parse the page content
    soup = BeautifulSoup(guild_page_raw.text, 'html.parser')

    # Find the div with the class 'raids_week'
    raids_week_div = soup.find('div', class_='raids_week')
    
    # Extract the text inside the div (if it exists)
    if raids_week_div:
        raids_week_value = raids_week_div.text.strip()
        # Remove the "Raids per week: " prefix to keep only the number
        raids_week_value = raids_week_value.replace('Raids per week: ', '')
    else:
        raids_week_value = 'N/A'  # Set a default value if the div is not found

    # Append the extracted value to the list
    raids_week_values.append(raids_week_value)

    # Wait for 1 second to avoid overloading the webserver
    time.sleep(1)

# Add the new 'Raids Week' column to the DataFrame
df['Raids Week'] = raids_week_values

# Reorder the columns so that 'Raids Week' comes before 'Link'
df = df[['Rank', 'Guild Name', 'Realm', 'Raids Week', 'Link']]

# Save the updated DataFrame to a new CSV file
output_csv = 'wowprogress_guilds_with_raids_week_2000.csv'
df.to_csv(output_csv, index=False, encoding='utf-8')

print(f"CSV file '{output_csv}' created successfully!")
