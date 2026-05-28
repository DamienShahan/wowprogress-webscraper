from bs4 import BeautifulSoup
import pandas as pd
import os
from pathlib import Path


def get_downloads_folder():
    return Path(__file__).resolve().parent / "downloads/overview"


def get_html_files(folder):
    html_files = []

    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() in [".htm", ".html"]:
            if file.stem.isdigit():
                html_files.append(file)

    return sorted(html_files, key=lambda file: int(file.stem))


def normalize_guild_link(href):
    if not href:
        return ""

    if href.startswith("/"):
        return f"https://www.wowprogress.com{href}"

    return href


def should_exclude_realm(guild_realm):
    excluded_prefixes = [
        "US",
        "EU (RU)",
        "EU (FR)",
        "OC",
    ]

    return any(guild_realm.startswith(prefix) for prefix in excluded_prefixes)


# Create output folder if it does not exist
os.makedirs("output", exist_ok=True)

downloads_folder = get_downloads_folder()

if not downloads_folder.exists():
    print(f"Downloads folder not found: {downloads_folder}")
    raise SystemExit(1)

html_files = get_html_files(downloads_folder)

if not html_files:
    print(f"No numbered .htm/.html files found in: {downloads_folder}")
    raise SystemExit(1)

print(f"Found {len(html_files)} HTML files.")

guilds = []

for html_file in html_files:
    print(f"Parsing file: {html_file.name}")

    with open(html_file, "r", encoding="utf-8", errors="replace") as file:
        html = file.read()

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", {"class": "rating"})

    if table is None:
        print(f"No rating table found in {html_file.name}. Skipping.")
        continue

    rows = table.find_all("tr")

    file_guild_count = 0

    for row in rows[1:]:
        rank_tag = row.find("span", class_="rank")
        guild_tag = row.find("a", class_="guild")
        realm_tag = row.find("a", class_="realm")

        if not rank_tag or not guild_tag or not realm_tag:
            continue

        rank_text = rank_tag.text.strip()

        if not rank_text.isdigit():
            continue

        rank = int(rank_text)
        guild_name = guild_tag.text.strip()
        guild_realm = realm_tag.text.strip()
        guild_link = normalize_guild_link(guild_tag.get("href", ""))

        if should_exclude_realm(guild_realm):
            continue

        guilds.append({
            "Rank": rank,
            "Guild Name": guild_name,
            "Realm": guild_realm,
            "Link": guild_link,
        })

        file_guild_count += 1

    print(f"Found {file_guild_count} guilds in {html_file.name}.")


df = pd.DataFrame(guilds)

if not df.empty:
    df = df.sort_values(by=["Rank", "Guild Name", "Realm"])

output_path = "output/wowprogress_guild_list.csv"
df.to_csv(output_path, index=False, encoding="utf-8")

print(f"CSV file '{output_path}' created successfully!")
print(f"Extracted {len(df)} guild rows from {len(html_files)} files.")