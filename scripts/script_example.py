import asyncio
import json
from datetime import datetime
import re

from common.telegram_client import create_client
from common.file_types import is_book_file

from config import (
    SOURCE_CHAT,
    DATE_FROM,
    DATE_TO,
    OUTPUT_DIR
)

async def main():
    client = create_client()

    try:
        await client.start()

        # Здесь остаётся твой код сбора файлов:
        # date_from, date_to, files,
        # async for message in client.iter_messages(...)
        # формирование item и запись JSON

    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())