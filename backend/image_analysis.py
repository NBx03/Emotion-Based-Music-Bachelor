import os
import json
import tempfile
import numpy as np
from image_processing import load_dataset, calculate_centroids, determine_emotion, calculate_brightness, calculate_colorfulness, detect_objects, detect_faces

EMOSET_CENTROIDS = None

EMOSET_IMAGE_PATH = os.environ.get("EMOSET_IMAGE_PATH", "D:/EmoSet/image")
EMOSET_ANNOTATION_PATH = os.environ.get("EMOSET_ANNOTATION_PATH", "D:/EmoSet/annotation")

_DEFAULT_CENTROIDS_PATH = os.path.join(os.path.dirname(__file__), "data", "emoset_centroids.json")
EMOSET_CENTROIDS_PATH = os.environ.get("EMOSET_CENTROIDS_PATH", _DEFAULT_CENTROIDS_PATH)


def load_centroids_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {emotion: np.array(vector, dtype=np.float32) for emotion, vector in raw.items()}


def save_centroids_to_file(centroids, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    serializable = {emotion: np.asarray(vector).tolist() for emotion, vector in centroids.items()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f)


def load_emoset():
    """
    Возвращает центроиды эмоций CLIP-эмбеддингов.
    Если рядом лежит предподсчитанный файл (EMOSET_CENTROIDS_PATH,
    см. scripts/precompute_centroids.py) — грузит его. Иначе считает
    центроиды из полного датасета EmoSet (нужны EMOSET_IMAGE_PATH /
    EMOSET_ANNOTATION_PATH) и кэширует результат в этот файл.
    """
    global EMOSET_CENTROIDS
    if EMOSET_CENTROIDS is None:
        if os.path.exists(EMOSET_CENTROIDS_PATH):
            EMOSET_CENTROIDS = load_centroids_from_file(EMOSET_CENTROIDS_PATH)
        else:
            max_images_per_emotion = 100
            dataset = load_dataset(EMOSET_IMAGE_PATH, EMOSET_ANNOTATION_PATH, max_images_per_emotion)
            EMOSET_CENTROIDS = calculate_centroids(dataset)
            save_centroids_to_file(EMOSET_CENTROIDS, EMOSET_CENTROIDS_PATH)
    return EMOSET_CENTROIDS

def analyze_image(image_bytes: bytes) -> dict:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name
    try:
        centroids = load_emoset()
        emotion = determine_emotion(tmp_path, centroids)
        brightness = calculate_brightness(tmp_path)
        colorfulness = calculate_colorfulness(tmp_path)
        objects = detect_objects(tmp_path, 0.8)
        face_count = detect_faces(tmp_path)
        return {
            "emotion": emotion,
            "brightness": brightness,
            "colorfulness": colorfulness,
            "objects": objects,
            "face_count": face_count
        }
    finally:
        os.remove(tmp_path)
