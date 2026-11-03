import asyncio
import json
from datetime import datetime
import re

from common.telegram_client import create_client
from common.file_types import is_book_file

from config import (
    SOURCE_CHAT,
    TARGET_CHAT
)

# INPUT_FILE - файл список постов на репост
INPUT_FILE = "data/filtered/Filtered_Переходник канал_from2026-10-07_to2026-10-10.json"

# Стоп айди. Репост закончится когда дойдет до файла с этим айди
idp = 10

async def main():
    client = create_client()

    try:
        await client.start()

        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            files = json.load(f)

        flen = len(files)

        print(f"Файлов для отправки: {flen}")

        for item in files:
            if item["id"] < idp:
                continue

            if item["id"] % 1000 == 0:
                await asyncio.sleep(60)

            message_id = item["message_id"]
            filename = item["filename"]

            try:
                # Получаем исходное сообщение
                message = await client.get_messages(
                    SOURCE_CHAT,
                    ids=message_id
                )

                if not message:
                    print("  Сообщение не найдено")
                    continue

                if not message.media:
                    print("  В сообщении нет медиа")
                    continue

                print(f"Отправляю {item['id']}/{flen}: {filename}")

                # Отправляем существующий Telegram-файл
                # без скачивания его на компьютер
                await client.send_file(
                    TARGET_CHAT,
                    message.media,
                    caption=filename
                )

                print("  OK")

            except Exception as e:
                print(f"  ОШИБКА: {e}")
                return

            # Небольшая задержка
            await asyncio.sleep(0.1)

    finally:
        await client.disconnect()
        print("Готово!")


if __name__ == "__main__":
    asyncio.run(main())