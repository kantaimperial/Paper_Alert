import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

GEMINI_MODEL_DEFAULT = "gemini-3.1-flash-lite"
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", GEMINI_MODEL_DEFAULT)

STATE_DIR = ROOT_DIR / "state"
STATE_FILE = STATE_DIR / "last_run.json"

# How many days back to search when no prior run state exists.
LOOKBACK_DAYS_DEFAULT = 7

CROSSREF_MAILTO = GMAIL_ADDRESS or "example@example.com"
