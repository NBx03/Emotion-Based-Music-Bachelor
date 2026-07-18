#!/usr/bin/env python
"""
Предподсчитывает центроиды эмоций (усреднённые CLIP-эмбеддинги по каждому
классу эмоции) из датасета EmoSet и сохраняет их в JSON-файл, который
backend грузит при старте вместо пересчёта из полного датасета.

Запускать вручную на машине, где физически лежит датасет EmoSet, и там
же, где установлены тяжёлые ML-зависимости backend'а
(backend/requirements.txt: torch, transformers и т.д.).

Пример:
    python scripts/precompute_centroids.py \
        --image-path D:/EmoSet/image \
        --annotation-path D:/EmoSet/annotation \
        --output backend/data/emoset_centroids.json

Без аргументов использует те же переменные окружения / дефолты, что и
backend/image_analysis.py (EMOSET_IMAGE_PATH, EMOSET_ANNOTATION_PATH,
EMOSET_CENTROIDS_PATH).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from image_processing import load_dataset, calculate_centroids
from image_analysis import (
    EMOSET_IMAGE_PATH as DEFAULT_IMAGE_PATH,
    EMOSET_ANNOTATION_PATH as DEFAULT_ANNOTATION_PATH,
    EMOSET_CENTROIDS_PATH as DEFAULT_CENTROIDS_PATH,
    save_centroids_to_file,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--image-path", default=DEFAULT_IMAGE_PATH, help="Путь к EmoSet/image")
    parser.add_argument("--annotation-path", default=DEFAULT_ANNOTATION_PATH, help="Путь к EmoSet/annotation")
    parser.add_argument("--output", default=DEFAULT_CENTROIDS_PATH, help="Куда сохранить centroids JSON")
    parser.add_argument("--max-images-per-emotion", type=int, default=100)
    args = parser.parse_args()

    print(f"Loading dataset from {args.image_path} / {args.annotation_path} ...")
    dataset = load_dataset(args.image_path, args.annotation_path, args.max_images_per_emotion)
    print(f"Loaded {len(dataset)} (embedding, annotation) pairs. Computing centroids...")
    centroids = calculate_centroids(dataset)

    save_centroids_to_file(centroids, args.output)
    print(f"Saved {len(centroids)} centroids to {args.output}")


if __name__ == "__main__":
    main()
