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

INPUT_CSV = "output/wowprogress_guild_list.csv"
OUTPUT_CSV = "output/wowprogress_guild_content.csv"
FILTER_LANGUAGES = ["German", "English"]
REQUEST_DELAY_SECONDS = 0.5
OPENAI_MODEL = "gpt-5-nano"

WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]

scraper = cloudscraper.create_scraper()