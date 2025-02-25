import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import openai
import json
import yaml
import re

# Load secrets from YAML
with open("secrets.yaml", "r", encoding="utf-8") as f:
    secrets = yaml.safe_load(f)
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

# Define languages to filter for
FILTER_LANGUAGES = ["German", "English"]

# Create a CloudScraper instance
scraper = cloudscraper.create_scraper()

# Read the existing CSV file
input_csv = 'wowprogress_guilds_with_ranks_filtered_to_2000.csv'
df = pd.read_csv(input_csv)
total_rows = len(df)

# Initialize lists to store extracted values
raids_week_values = []
language_values = []
raid_days_json_values = []

# Function to call OpenAI and extract raid days
def get_raid_days(guild_description):
    if not guild_description or guild_description.strip() == "":
        return json.dumps([])  # Return empty list if no description
    
    prompt = f"""
    Extract only the raid days, or the fact that the guild no longer raids, from the following guild description.
    
    Return the response as a valid JSON list with only the raid days, like this:
    ["Monday", "Tuesday", "Wednesday"]

    If the guild no longer actively raids, return a list containing a single string with the value "Dead", like this:
    ["Dead"]
    
    Ensure that:
    - The output is a strict JSON list.
    - The weekdays are in English.
    - Do not include any additional text, explanations, or formatting.
    
    Guild Description:
    {guild_description}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant that extracts raid schedules from guild descriptions."},
                      {"role": "user", "content": prompt}],
            api_key=OPENAI_API_KEY
        )
        
        # Extract and parse JSON from ChatGPT response
        ai_response = response["choices"][0]["message"]["content"].strip()
        
        # Clean the response to extract only content inside [ and ]
        match = re.search(r"\[.*?\]", ai_response, re.DOTALL)  # Find content between square brackets
        if match:
            cleaned_response = match.group(0)  # Extract the matched list
        else:
            cleaned_response = "[]"  # Default to an empty list if no match found

        return cleaned_response

    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return json.dumps([])  # Return empty list in case of error

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    guild_link = row['Link']
    
    print(f"{index+1}/{total_rows}: Fetching data for {row['Guild Name']}")

    # Fetch the guild's page
    guild_page_raw = scraper.get(guild_link)
    
    # Parse the page content
    soup = BeautifulSoup(guild_page_raw.text, 'html.parser')

    # Extract 'raids_week' information
    raids_week_div = soup.find('div', class_='raids_week')
    raids_week_value = raids_week_div.text.strip().replace('Raids per week: ', '') if raids_week_div else 'N/A'

    # Extract 'language' information
    language_div = soup.find('div', class_='language')
    language_value = language_div.text.strip().replace('Primary Language: ', '') if language_div else 'N/A'

    # Extract 'guildDescription' information
    description_div = soup.find('div', class_='guildDescription')
    guild_description = description_div.text.strip() if description_div else ""

    # Call ChatGPT to analyze raid days
    raid_days_json = get_raid_days(guild_description)
    #print(f"Extracted raid days: {raid_days_json}")

    # Append the extracted values
    raids_week_values.append(raids_week_value)
    language_values.append(language_value)
    raid_days_json_values.append(raid_days_json)

    # Wait to avoid overloading the webserver
    time.sleep(1)

# Add new columns to the DataFrame
df['Raids Week'] = raids_week_values
df['Language'] = language_values
df['Raid Days JSON'] = raid_days_json_values

# Filter DataFrame based on the user-defined FILTER_LANGUAGES
df_filtered = df[df['Language'].isin(FILTER_LANGUAGES)].copy()

# Parse Raid Days JSON and create individual columns for each day of the week
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Dead"]

# Initialize new columns with False
df_filtered = df_filtered.assign(**{day: False for day in days_of_week})

# Fill in the raid days based on the list response
for index, row in df_filtered.iterrows():
    try:
        raid_days_list = json.loads(row["Raid Days JSON"])
        for day in raid_days_list:
            if day in days_of_week:
                df_filtered.loc[index, day] = True
    except json.JSONDecodeError:
        print(f"Error decoding JSON for row {index}")

# Drop the JSON column as it's no longer needed
df_filtered = df_filtered.drop(columns=["Raid Days JSON"])

# Reorder columns for better readability
columns_order = ['Rank', 'Guild Name', 'Realm', 'Raids Week', 'Language'] + days_of_week + ['Link']
df_filtered = df_filtered[columns_order]

# Save the filtered DataFrame to a new CSV file
output_csv = 'wowprogress_guilds_filtered_with_raiddays_openai.csv'
df_filtered.to_csv(output_csv, index=False, encoding='utf-8')

print(f"Filtered CSV file '{output_csv}' created successfully! Included languages: {FILTER_LANGUAGES}")
