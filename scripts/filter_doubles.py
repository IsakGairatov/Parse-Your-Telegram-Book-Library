import json
from pathlib import Path

from config import BASE_DIR

# SOURCE_FILE - файл, в котором ищем дубли
# EXISTING_FILE - файл, в котором проверяем наличие
# OUTPUT_FILE - файл, в который сохраняем результат


SOURCE_FILE = BASE_DIR / "data/Переходник канал/Переходник канал_from2026-10-07_to2026-10-10.json"
EXISTING_FILE = BASE_DIR /"data/Мои файлики/Мои файлики_from2026-09-16_to2026-09-19.json"
OUTPUT_FILE = BASE_DIR / "data/filtered" / f"Filtered_{SOURCE_FILE.name}"
DUPLICATES_FILE = BASE_DIR / "data/duplicates" / f"Existing_{SOURCE_FILE.name}"

def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    source = load_json(SOURCE_FILE)
    existing = load_json(EXISTING_FILE)

    # Собираем все существующие файлы из второго JSON
    existing_files = {
        (item.get("filename"), item.get("size"))
        for item in existing
    }

    result = []
    added_files = set()
    duplicates = []

    for item in source:
        key = (item.get("filename"), item.get("size"))

        if key in existing_files:
            duplicates.append(item.copy())

        elif key not in added_files:
            new_item = item.copy()
            new_item["id"] = len(result) + 1
            result.append(new_item)
            added_files.add(key)

    # Создаём папку для фильтрованных и дубликатов
    output_dir1 = BASE_DIR/"data/filtered"
    output_dir2 = BASE_DIR/"data/duplicates"
    output_dir1.mkdir(parents=True, exist_ok=True)
    output_dir2.mkdir(parents=True, exist_ok=True)

    # Сохраняем третий JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=4
        )

    with open(DUPLICATES_FILE, "w", encoding="utf-8") as f:
        json.dump(
            duplicates,
            f,
            ensure_ascii=False,
            indent=4
        )

    print(f"В первом JSON: {len(source)}")
    print(f"Во втором JSON: {len(existing)}")
    print(f"Добавлено в третий JSON: {len(result)}")
    print(f"Пропущено как уже существующие: {len(source) - len(result)}")


if __name__ == "__main__":
    main()