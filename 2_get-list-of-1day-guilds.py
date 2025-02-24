import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time  # Import the time module for sleep

# Define languages to filter for
FILTER_LANGUAGES = ["German", "English"]  # Modify this list as needed

# Create a CloudScraper instance
scraper = cloudscraper.create_scraper()

# Read the existing CSV file
input_csv = 'wowprogress_guilds_with_ranks_filtered_to_2000.csv'
df = pd.read_csv(input_csv)
total_rows = len(df)

# Initialize lists to store extracted values
raids_week_values = []
language_values = []

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    guild_link = row['Link']
    
    print(f"{index}/{total_rows}: Fetching data for {row['Guild Name']}...")

    # Fetch the guild's page using the link
    guild_page_raw = scraper.get(guild_link)
    
    # Parse the page content
    soup = BeautifulSoup(guild_page_raw.text, 'html.parser')

    # Find the div with the class 'raids_week'
    raids_week_div = soup.find('div', class_='raids_week')
    
    # Find the div with the class 'language'
    language_div = soup.find('div', class_='language')
    
    # Extract the text inside the raids_week div (if it exists)
    if raids_week_div:
        raids_week_value = raids_week_div.text.strip().replace('Raids per week: ', '')
    else:
        raids_week_value = 'N/A'  # Default value if not found
        
    # Extract the text inside the language div (if it exists)
    if language_div:
        language_value = language_div.text.strip().replace('Primary Language: ', '')
    else:
        language_value = 'N/A'  # Default value if not found

    # Append the extracted values to the lists
    raids_week_values.append(raids_week_value)
    language_values.append(language_value)

    # Wait for 1 second to avoid overloading the webserver
    time.sleep(1)

# Add new columns to the DataFrame
df['Raids Week'] = raids_week_values
df['Language'] = language_values

# Filter DataFrame based on the user-defined FILTER_LANGUAGES
df_filtered = df[df['Language'].isin(FILTER_LANGUAGES)]

# Reorder columns for better readability
df_filtered = df_filtered[['Rank', 'Guild Name', 'Realm', 'Raids Week', 'Language', 'Link']]

# Save the filtered DataFrame to a new CSV file
output_csv = 'wowprogress_guilds_filtered_weeks_languages.csv'
df_filtered.to_csv(output_csv, index=False, encoding='utf-8')

print(f"Filtered CSV file '{output_csv}' created successfully! Included languages: {FILTER_LANGUAGES}")
