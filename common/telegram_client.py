from telethon import TelegramClient

from config import API_ID, API_HASH, SESSION, BASE_DIR


def create_client():
    session_path = BASE_DIR / SESSION

    return TelegramClient(
        str(session_path),
        API_ID,
        API_HASH,
    )