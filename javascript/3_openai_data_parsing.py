import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import unquote, urlparse

import pandas as pd
import yaml
from openai import OpenAI

# ============================================================
# Configuration
# ============================================================

INPUT_JSON_DIR = "./downloads/guild_content"
OUTPUT_CSV = "output/wowprogress_guilds_filtered_with_schedule_openai.csv"

FILTER_LANGUAGES = ["German", "English"]

# Set to an integer for testing, e.g. 5.
# Set to None to process all guilds.
TEST_LIMIT: Optional[int] = None

REQUEST_DELAY_SECONDS = 0.5
OPENAI_MODEL = "gpt-5.4-nano"

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


# ============================================================
# Helpers
# ============================================================

def safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


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


def extract_realm_from_url(url: str) -> str:
    """
    Extract realm from a WowProgress URL.

    Example:
    https://www.wowprogress.com/guild/eu/draenor/Ascendance
    -> EU-Draenor
    """
    url = safe_text(url)
    if not url:
        return ""

    try:
        path_parts = [part for part in urlparse(url).path.split("/") if part]

        # Expected format:
        # guild / eu / draenor / GuildName
        if len(path_parts) >= 3 and path_parts[0] == "guild":
            region = path_parts[1].upper()
            realm = unquote(path_parts[2]).replace("+", " ")
            return f"{region}-{realm.title()}"

    except Exception:
        pass

    return ""


# ============================================================
# JSON loading
# ============================================================

def load_guild_records_from_json_files(input_dir: str) -> List[Dict[str, Any]]:
    """
    Read all .json files in the input directory.

    Supports files containing either:
    - a single JSON object
    - a list of JSON objects
    """
    input_path = Path(input_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Input JSON directory does not exist: {input_dir}")

    json_files = sorted(
        file_path
        for file_path in input_path.iterdir()
        if file_path.is_file() and file_path.suffix.lower() == ".json"
    )

    if not json_files:
        raise FileNotFoundError(f"No .json files found in: {input_dir}")

    records: List[Dict[str, Any]] = []

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                data["_source_file"] = json_file.name
                records.append(data)

            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        item["_source_file"] = json_file.name
                        records.append(item)
                    else:
                        print(f"Skipping non-object item in {json_file.name}")

            else:
                print(f"Skipping {json_file.name}: expected object or list of objects")

        except Exception as e:
            print(f"Error reading {json_file.name}: {e}")

    return records


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
                "required": WEEKDAYS,
            },
            "extra_raid_day": {"type": "string"},
            "extra_raid_day_period": {"type": "string"},
        },
        "required": [
            "dead",
            "schedule",
            "extra_raid_day",
            "extra_raid_day_period",
        ],
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
# Row processing
# ============================================================

def process_record(record: Dict[str, Any], index: int, total_rows: int) -> Dict[str, Any]:
    guild_name = safe_text(record.get("guild_name", ""))
    guild_link = safe_text(record.get("url", ""))
    language = safe_text(record.get("language", ""))
    raids_week = safe_text(record.get("raids_per_week", ""))
    guild_description = safe_text(record.get("description", ""))

    print(f"{index + 1}/{total_rows}: Extracting schedule for {guild_name}")

    schedule_data = extract_schedule_with_openai(guild_description)

    return {
        "Rank": safe_text(record.get("rank", "")),
        "Guild Name": guild_name,
        "Realm": safe_text(record.get("realm", "")) or extract_realm_from_url(guild_link),
        "Raids Week": raids_week,
        "Language": language,
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
        "Link": guild_link,
        "Source File": safe_text(record.get("_source_file", "")),
    }


def build_failed_record(record: Dict[str, Any]) -> Dict[str, Any]:
    guild_link = safe_text(record.get("url", ""))

    return {
        "Rank": safe_text(record.get("rank", "")),
        "Guild Name": safe_text(record.get("guild_name", "")),
        "Realm": safe_text(record.get("realm", "")) or extract_realm_from_url(guild_link),
        "Raids Week": safe_text(record.get("raids_per_week", "")),
        "Language": safe_text(record.get("language", "")),
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
        "Link": guild_link,
        "Source File": safe_text(record.get("_source_file", "")),
    }


# ============================================================
# Main
# ============================================================

def main() -> None:
    records = load_guild_records_from_json_files(INPUT_JSON_DIR)

    loaded_rows = len(records)
    print(f"Loaded {loaded_rows} guild records from JSON files in {INPUT_JSON_DIR}")

    if TEST_LIMIT is not None:
        records = records[:TEST_LIMIT]
        print(f"TEST_LIMIT is active: only processing the first {TEST_LIMIT} guilds")
    else:
        print("TEST_LIMIT is disabled: processing all guilds")

    total_rows = len(records)

    extracted_rows: List[Dict[str, Any]] = []

    for index, record in enumerate(records):
        try:
            extracted = process_record(record, index, total_rows)
        except Exception as e:
            print(f"Error processing record {index} ({record.get('guild_name', '')}): {e}")
            extracted = build_failed_record(record)

        extracted_rows.append(extracted)
        time.sleep(REQUEST_DELAY_SECONDS)

    df_out = pd.DataFrame(extracted_rows)

    # Keep only selected languages.
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
        "Source File",
    ]

    ordered_columns = [col for col in ordered_columns if col in df_out.columns]
    df_out = df_out[ordered_columns]

    output_path = Path(OUTPUT_CSV)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df_out.to_csv(output_path, index=False, encoding="utf-8")

    print(
        f"Filtered CSV file '{OUTPUT_CSV}' created successfully! "
        f"Included languages: {FILTER_LANGUAGES}"
    )


if __name__ == "__main__":
    main()