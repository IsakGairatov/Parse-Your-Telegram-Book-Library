import asyncio
import json
from datetime import datetime
import re

from Collect_your_tg_library.common.telegram_client import create_client
from Collect_your_tg_library.common.file_types import is_book_file

from Collect_your_tg_library.config import (
    SOURCE_CHAT,
    DATE_FROM,
    DATE_TO,
    OUTPUT_FILE,
)

async def main():
    client = create_client()

    try:
        await client.start()

        chat = await client.get_entity(SOURCE_CHAT)

        chat_name = (
                getattr(chat, "title", None)
                or getattr(chat, "username", None)
                or str(SOURCE_CHAT)
        )

        # Убираем символы, которые нельзя использовать в именах папок
        safe_chat_name = re.sub(
            r'[<>:"/\\|?*\x00-\x1f]',
            "_",
            chat_name,
        ).strip(" .") or "Unknown_chat"

        date_from = datetime.fromisoformat(DATE_FROM)
        date_to = datetime.fromisoformat(DATE_TO)

        files = []

        print("Ищу файлы...")

        async for message in client.iter_messages(
                SOURCE_CHAT,
                reverse=True
        ):
            if not message.date:
                continue

            message_date = message.date.replace(tzinfo=None)

            if message_date < date_from:
                continue

            if message_date >= date_to:
                break

            # Проверяем, есть ли документ/файл
            if not message.document:
                continue

            filename = None

            # Пытаемся получить настоящее имя файла
            if message.file:
                filename = message.file.name

            if not filename:
                filename = "Без названия"

            if not is_book_file(filename):
                continue

            item = {
                "id": len(files) + 1,
                "chat_id": SOURCE_CHAT,
                "message_id": message.id,
                "filename": filename,
                "size": message.document.size,
                "date": message_date.isoformat(),
            }

            files.append(item)

            print(
                f"[{item['id']}] "
                f"{message_date} — {filename}"
            )

        # Определяем даты самого раннего и последнего файлов
        if files:
            first_date = datetime.fromisoformat(
                files[0]["date"]
            ).strftime("%Y-%m-%d")

            last_date = datetime.fromisoformat(
                files[-1]["date"]
            ).strftime("%Y-%m-%d")
        else:
            first_date = DATE_FROM
            last_date = DATE_TO

        # Создаём папку с названием чата
        output_dir = OUTPUT_FILE.parent / safe_chat_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Формируем имя JSON
        output_file = output_dir / (
            f"{safe_chat_name}_from{first_date}_to{last_date}.json"
        )

        # Сохраняем результат
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(
                files,
                f,
                ensure_ascii=False,
                indent=4,
            )

        print()
        print(f"Готово. Найдено файлов: {len(files)}")
        print(f"Сохранено в {output_file}")

    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
