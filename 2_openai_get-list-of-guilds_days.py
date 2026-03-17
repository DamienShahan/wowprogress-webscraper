import json
import re
import time
from typing import Any, Dict, List, Optional

import cloudscraper
import pandas as pd
import yaml
from bs4 import BeautifulSoup
from openai import OpenAI

# ============================================================
# Configuration
# ============================================================

INPUT_CSV = "wowprogress_guilds_to_analyze.csv"
OUTPUT_CSV = "wowprogress_guilds_filtered_with_schedule_openai.csv"
FILTER_LANGUAGES = ["German", "English"]
REQUEST_DELAY_SECONDS = 0.5
OPENAI_MODEL = "gpt-5-nano"

WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]

# ============================================================
# Secrets / Clients
# ============================================================

with open("secrets.yaml", "r", encoding="utf-8") as f:
    secrets = yaml.safe_load(f)

OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)
scraper = cloudscraper.create_scraper()


# ============================================================
# Helpers
# ============================================================

def safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def extract_text(soup: BeautifulSoup, class_name: str, prefix_to_strip: Optional[str] = None) -> str:
    div = soup.find("div", class_=class_name)
    if not div:
        return ""
    text = div.get_text("\n", strip=True)
    if prefix_to_strip and text.startswith(prefix_to_strip):
        text = text[len(prefix_to_strip):].strip()
    return text


def clean_time_range(value: str) -> str:
    """
    Normalize time ranges like:
    '19:00 - 23:15' -> '19:00-23:15'
    """
    value = safe_text(value)
    if not value:
        return ""
    value = re.sub(r"\s*-\s*", "-", value)
    return value


def build_empty_schedule_result() -> Dict[str, Any]:
    return {
        "dead": False,
        "schedule": {day: "" for day in WEEKDAYS},
        "extra_raid_day": "",
        "extra_raid_day_period": "",
    }


def try_parse_json_object(text: str) -> Dict[str, Any]:
    """
    Try to extract and parse a JSON object from model output.
    """
    text = safe_text(text)
    if not text:
        return {}

    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}

    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def normalize_ai_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Force the model result into the shape expected by the CSV builder.
    """
    normalized = build_empty_schedule_result()

    if not isinstance(result, dict):
        return normalized

    normalized["dead"] = bool(result.get("dead", False))

    schedule = result.get("schedule", {})
    if isinstance(schedule, dict):
        for day in WEEKDAYS:
            normalized["schedule"][day] = clean_time_range(schedule.get(day, ""))

    normalized["extra_raid_day"] = safe_text(result.get("extra_raid_day", ""))
    normalized["extra_raid_day_period"] = safe_text(result.get("extra_raid_day_period", ""))

    return normalized


# ============================================================
# OpenAI extraction
# ============================================================

def extract_schedule_with_openai(guild_description: str) -> Dict[str, Any]:
    """
    Extract schedule information from guild description.

    Returns:
    {
      "dead": bool,
      "schedule": {
        "Monday": "",
        "Tuesday": "20:00-23:00",
        ...
      },
      "extra_raid_day": "Sunday",
      "extra_raid_day_period": "3 weeks"
    }
    """
    if not safe_text(guild_description):
        return build_empty_schedule_result()

    schema_description = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "dead": {"type": "boolean"},
            "schedule": {
                "type": "object",
                "additionalProperties": False,
                "properties": {day: {"type": "string"} for day in WEEKDAYS},
                "required": WEEKDAYS
            },
            "extra_raid_day": {"type": "string"},
            "extra_raid_day_period": {"type": "string"},
        },
        "required": [
            "dead",
            "schedule",
            "extra_raid_day",
            "extra_raid_day_period",
        ]
    }

    prompt = f"""
Extract the guild's planned raid schedule from the guild description below.

Return ONLY a JSON object matching this exact schema:
{json.dumps(schema_description, ensure_ascii=False, indent=2)}

Rules:
1. Use English weekday names exactly:
   Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday

2. For "schedule":
   - Put the planned raid time for each weekday.
   - Use format HH:MM-HH:MM
   - If the guild does not raid on that day, use an empty string.
   - Example:
     "Tuesday": "20:00-23:00"

3. If a day is only an extra / temporary / limited-duration raid day:
   - Still put its time into that day's schedule field.
   - Also populate:
     - "extra_raid_day"
     - "extra_raid_day_period"

4. "extra_raid_day_period" examples:
   - "3 weeks"
   - "2 weeks"
   - "end of progression"
   - ""
   If there is no extra raid day, leave both extra-raid-day fields empty.

5. If the guild is dead / no longer raids actively:
   - Set "dead": true
   - Leave all schedule days empty strings unless a current active schedule is explicitly stated.

6. Do not invent details. If something is unclear, leave it empty.

Guild Description:
{guild_description}
"""

    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You extract raid schedules from World of Warcraft guild descriptions. "
                        "Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        raw_text = getattr(response, "output_text", "") or ""
        parsed = try_parse_json_object(raw_text)
        return normalize_ai_result(parsed)

    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return build_empty_schedule_result()


# ============================================================
# Scraping
# ============================================================

def scrape_guild_page(guild_link: str) -> Dict[str, str]:
    response = scraper.get(guild_link, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    raids_week = extract_text(soup, "raids_week", "Raids per week: ")
    language = extract_text(soup, "language", "Primary Language: ")
    guild_description = extract_text(soup, "guildDescription")

    return {
        "raids_week": raids_week or "",
        "language": language or "",
        "guild_description": guild_description or "",
    }


# ============================================================
# Row processing
# ============================================================

def process_row(row: pd.Series, index: int, total_rows: int) -> Dict[str, Any]:
    guild_name = safe_text(row.get("Guild Name", ""))
    guild_link = safe_text(row.get("Link", ""))

    print(f"{index + 1}/{total_rows}: Fetching data for {guild_name}")

    scraped = scrape_guild_page(guild_link)
    schedule_data = extract_schedule_with_openai(scraped["guild_description"])

    return {
        "Raids Week": scraped["raids_week"],
        "Language": scraped["language"],
        "Dead": schedule_data["dead"],
        "Monday": schedule_data["schedule"]["Monday"],
        "Tuesday": schedule_data["schedule"]["Tuesday"],
        "Wednesday": schedule_data["schedule"]["Wednesday"],
        "Thursday": schedule_data["schedule"]["Thursday"],
        "Friday": schedule_data["schedule"]["Friday"],
        "Saturday": schedule_data["schedule"]["Saturday"],
        "Sunday": schedule_data["schedule"]["Sunday"],
        "Extra Raid Day": schedule_data["extra_raid_day"],
        "Extra Raid Day Period": schedule_data["extra_raid_day_period"],
    }


# ============================================================
# Main
# ============================================================

def main() -> None:
    df = pd.read_csv(INPUT_CSV)
    total_rows = len(df)

    extracted_rows: List[Dict[str, Any]] = []

    for index, row in df.iterrows():
        try:
            extracted = process_row(row, index, total_rows)
        except Exception as e:
            print(f"Error processing row {index} ({row.get('Guild Name', '')}): {e}")
            extracted = {
                "Raids Week": "",
                "Language": "",
                "Dead": False,
                "Monday": "",
                "Tuesday": "",
                "Wednesday": "",
                "Thursday": "",
                "Friday": "",
                "Saturday": "",
                "Sunday": "",
                "Extra Raid Day": "",
                "Extra Raid Day Period": "",
            }

        extracted_rows.append(extracted)
        time.sleep(REQUEST_DELAY_SECONDS)

    extracted_df = pd.DataFrame(extracted_rows)

    df_out = pd.concat([df.reset_index(drop=True), extracted_df.reset_index(drop=True)], axis=1)
    df_out = df_out[df_out["Language"].isin(FILTER_LANGUAGES)].copy()

    ordered_columns = [
        "Rank",
        "Guild Name",
        "Realm",
        "Raids Week",
        "Language",
        "Dead",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "Extra Raid Day",
        "Extra Raid Day Period",
        "Link",
    ]

    ordered_columns = [col for col in ordered_columns if col in df_out.columns]
    df_out = df_out[ordered_columns]

    df_out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"Filtered CSV file '{OUTPUT_CSV}' created successfully! Included languages: {FILTER_LANGUAGES}")


if __name__ == "__main__":
    main()