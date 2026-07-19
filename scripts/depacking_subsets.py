import zipfile
import json
import os
from collections import defaultdict

ZIP_PATH = r"C:\Users\hopm1\Downloads\EmoSet-118K.zip"
OUTPUT_DIR = r"C:\EmoSet"
MAX_PER_EMOTION = 100

with zipfile.ZipFile(ZIP_PATH, "r") as zf:
    name_set = set(zf.namelist())

    with zf.open("train.json") as f:
        entries = json.load(f)

    # подстраховка: смотрим, что реально лежит внутри, прежде чем на это полагаться
    print("Тип:", type(entries), "| Пример первой записи:", entries[0])

    by_emotion = defaultdict(list)
    for entry in entries:
        emotion = entry[0]
        by_emotion[emotion].append(entry)

    to_extract = []
    for emotion, rows in by_emotion.items():
        chosen = rows[:MAX_PER_EMOTION]
        for row in chosen:
            img_path, ann_path = row[1], row[2]
            to_extract.append(img_path)
            to_extract.append(ann_path)
        print(f"{emotion}: взято {len(chosen)} из {len(rows)}")

    missing = [n for n in to_extract if n not in name_set]
    if missing:
        print(f"⚠ Не найдено в архиве: {len(missing)}, например {missing[:5]}")
        to_extract = [n for n in to_extract if n in name_set]

    print("Будет извлечено файлов:", len(to_extract))
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name in to_extract:
        zf.extract(name, OUTPUT_DIR)

print("Готово:", OUTPUT_DIR)