
import asyncio
from datetime import datetime, time, timezone
from pathlib import Path

from common.telegram_client import create_client
from common.file_types import is_book_file

from metadata.metadata_extraction.book import get_book_metadata

from config import (
    SOURCE_CHAT
)

# ============================================================
# CONFIG FIELDS
# ============================================================

DATE_FROM = "2026-09-05"
DATE_TO = "2026-11-05"

# ============================================================
# METADATA FIELDS
# ============================================================

METADATA_FIELDS = (
    "Filename:",
    "Size:",
    "Full Size:",
    "Format:",
    "Title:",
    "Authors:",
    "Date:",
)


# ============================================================
# HELPERS
# ============================================================

def parse_date(value, end_of_day=False):
    """
    Преобразует дату из config.py в UTC datetime.

    YYYY-MM-DD:
        начало дня или конец дня.

    ISO datetime:
        сохраняет указанное время.
    """

    if isinstance(value, datetime):
        result = value

    elif hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day"):
        result = datetime.combine(
            value,
            time.max if end_of_day else time.min
        )

    else:
        value = str(value).strip()

        try:
            result = datetime.fromisoformat(value)
        except ValueError:
            result = datetime.strptime(value, "%Y-%m-%d")

            if end_of_day:
                result = result.replace(
                    hour=23,
                    minute=59,
                    second=59,
                    microsecond=999999
                )

    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)

    return result.astimezone(timezone.utc)


def format_size(size: int) -> str:

    if size < 1024:
        return f"{size} B"

    if size < 1024 ** 2:
        return f"{size / 1024:.1f} KB"

    if size < 1024 ** 3:
        return f"{size / 1024 ** 2:.1f} MB"

    return f"{size / 1024 ** 3:.1f} GB"


def has_metadata_caption(caption: str) -> bool:
    """
    Проверяет наличие всех полей метаданных.
    """
    if not caption:
        return False

    caption = caption.casefold()

    return all(
        field.casefold() in caption
        for field in METADATA_FIELDS
    )


def make_caption(message, metadata: dict) -> str:

    # --------------------------------------------------------
    # Telegram metadata
    # --------------------------------------------------------

    filename = message.file.name or "Unknown"
    full_size = message.file.size or 0

    size = format_size(full_size)

    extension = Path(filename).suffix.lower().lstrip(".")
    file_format = extension or "Unknown"

    # --------------------------------------------------------
    # Extracted metadata
    # --------------------------------------------------------

    title = metadata.get("title") or "Unknown"
    author = metadata.get("author") or "Unknown"
    generated_at = metadata.get("generated_at") or "Unknown"

    # --------------------------------------------------------
    # Build caption
    # --------------------------------------------------------

    return (
        f"**Filename:** {filename}\n"
        f"**Title:** {title}\n"
        f"**Authors:** {author}\n"
        f"**Size:** {size}\n"
        f"**Full Size:** {full_size}\n"
        f"**Date:** {generated_at}\n"
        f"**Format:** {file_format}"
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    date_from = parse_date(DATE_FROM)
    date_to = parse_date(DATE_TO, end_of_day=True)

    client = create_client()

    processed = 0
    skipped = 0
    errors = 0

    try:

        await client.start()

        chat = await client.get_entity(SOURCE_CHAT)

        print("=" * 70)
        print("CAPTION METADATA UPDATER")
        print("=" * 70)

        print(f"Source:      {SOURCE_CHAT}")
        print(f"Date from:   {date_from}")
        print(f"Date to:     {date_to}")
        print("Direction:   Newest -> Oldest")
        print("=" * 70)

        # ====================================================
        # MESSAGE ITERATION
        # ====================================================

        async for message in client.iter_messages(
            chat,
            reverse=False
        ):

            # ------------------------------------------------
            # Date range
            # ------------------------------------------------

            if message.date < date_from:

                print(
                    f"\n[STOP] Reached DATE_FROM boundary "
                    f"at message {message.id}"
                )

                break

            if message.date > date_to:
                continue

            # ------------------------------------------------
            # Book files only
            # ------------------------------------------------

            if not message.file:
                continue

            if not is_book_file(message.file.name):
                continue

            filename = message.file.name or "Unknown"

            # ------------------------------------------------
            # Existing caption check
            # ------------------------------------------------

            if has_metadata_caption(message.message or ""):

                skipped += 1

                print(
                    f"[SKIP] ID={message.id} | "
                    f"Metadata already exists | {filename}"
                )

                continue

            # ------------------------------------------------
            # Get metadata
            # ------------------------------------------------

            print()
            print("-" * 70)
            print(f"[PROCESS] ID: {message.id}")
            print(f"Date: {message.date}")
            print(f"File: {filename}")

            try:

                metadata = await get_book_metadata(
                    client,
                    chat.id,
                    message.id
                )

            except Exception as e:

                errors += 1

                print(
                    f"[ERROR] Metadata extraction failed: {e}"
                )

                continue

            # ------------------------------------------------
            # Build caption
            # ------------------------------------------------

            caption = make_caption(
                message,
                metadata
            )

            # ------------------------------------------------
            # Update message
            # ------------------------------------------------

            try:

                await client.edit_message(
                    chat,
                    message.id,
                    caption,
                    parse_mode="md"
                )

                processed += 1

                print("[OK] Caption updated")

            except Exception as e:

                errors += 1

                print(
                    f"[ERROR] Caption update failed: {e}"
                )

    finally:

        await client.disconnect()

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("FINISHED")
    print("=" * 70)

    print(f"Processed: {processed}")
    print(f"Skipped:   {skipped}")
    print(f"Errors:    {errors}")

    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
