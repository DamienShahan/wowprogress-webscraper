# WoWProgress Guild Table Export

Small browser-console script to export guild data from a WoWProgress ranking table into CSV format.

The script reads the table and copies the extracted data directly to the clipboard.

The most current version is in the `/javascript/` folder

## Usage

1. Open the desired WoWProgress ranking page in your browser.
2. Open Developer Tools.
3. Go to the **Console** tab.
4. Paste the script.
5. Press **Enter**.
6. The CSV will be copied to your clipboard or a JSON file will be downloaded
7. Paste it into a `.csv` file.

## Notes

This script only extracts data from a page that is already loaded in your browser. It does not make automated requests to WoWProgress.

## Settings

### 1_wowprogress_get-list-of-guilds.js

This script extracts the list of guilds, page for page, as CSV data to your clipboard.

Entries starting with the following area codes are ignored:

- "US"
- "EU (RU)"
- "EU (FR)"
- "EU (ES)"
- "OC"
- "KR"
- "TW"

The final list has to be saved to a .CSV file. E.g. `/downloads/overview/list.csv`

### 2_wowprogress_content-scrapper.js

This browser-console script extracts profile data from a single WoWProgress guild page and downloads it as a JSON file named after the guild.

It reads the guild name from the page title, then extracts the guild language, raids per week, description, and current recruitment priorities from the guild profile section.

The downloaded JSON includes:

- `url`
- `guild_name`
- `language`
- `raids_per_week`
- `description`
- `recruitment`

The `recruitment` field is stored as an array of class/role/priority objects, making it easier to process or import later.

### 3_ai_analysis.py

Finally, the guild description data is analysed using chatgpt and the final CSV output is generated, to be then inserted into a google spreadsheet.
