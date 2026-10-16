import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
SESSION = BASE_DIR/"userbot.session"

SOURCE_CHAT = os.environ["MyChannel"]
if SOURCE_CHAT.isnumeric():
    SOURCE_CHAT = int(SOURCE_CHAT)

DATE_FROM = "2013-08-01"
DATE_TO = "2026-12-30"

from datetime import datetime

OUTPUT_FILE = BASE_DIR / (
    f"data/newfiles_{datetime.now():%Y-%m-%d_%H-%M-%S}.json"
)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


