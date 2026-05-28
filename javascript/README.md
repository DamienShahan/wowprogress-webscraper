# WoWProgress Guild Table Export

Small browser-console script to export guild data from a WoWProgress ranking table into CSV format.

The script reads the table and copies the extracted data directly to the clipboard.

## Output Format

The generated CSV has the following columns:

```csv
Rank,Guild Name,Realm,Link
```

## Usage

1. Open the desired WoWProgress ranking page in your browser.
2. Open Developer Tools.
3. Go to the **Console** tab.
4. Paste the script.
5. Press **Enter**.
6. The CSV will be copied to your clipboard.
7. Paste it into a `.csv` file.

## Notes

This script only extracts data from a page that is already loaded in your browser. It does not make automated requests to WoWProgress.
