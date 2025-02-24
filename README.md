# Wowprogress Webscrapper
This is a small script used to scrape the number of raid days from wowprogress to filter the choices to ones that fit the amount of days being looked for.

## Execution
Execute the three scripts after each other, in the order 1_ then 2_ then 3_.

## Settings

### 1_get-list-of-guilds.py
This script goes page for page and downloads a list of all guilds that raid 1-2 days per week, till the world rank 2000. Then all entries starting with `US`, `OC`, `EU (FR)` or `EU (RU)` are filtered out. The final list is saved to a .CSV file.

### 2_get-list-of-1day-guilds.py
This script takes the output from script 1 and looks up the number of raid days per week that each guild in the list has. The number of raids per week is then added to the list and output as a seperate .CSV file.
This step also filters out guilds that are not in the language that we are searching for.
Finally, the guild description is analysed using chatgpt and the specific raid days are set in the CSV output.

### 3_filter-for-1day.py
Finally, script 3 removes all rows where the number of raids per week does not match the value we are looking for.