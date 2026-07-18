import os
import tempfile
from image_processing import load_dataset, calculate_centroids, determine_emotion, calculate_brightness, calculate_colorfulness, detect_objects, detect_faces

EMOSET_CENTROIDS = None

EMOSET_IMAGE_PATH = os.environ.get("EMOSET_IMAGE_PATH", "D:/EmoSet/image")
EMOSET_ANNOTATION_PATH = os.environ.get("EMOSET_ANNOTATION_PATH", "D:/EmoSet/annotation")

def load_emoset():
    global EMOSET_CENTROIDS
    if EMOSET_CENTROIDS is None:
        max_images_per_emotion = 100
        dataset = load_dataset(EMOSET_IMAGE_PATH, EMOSET_ANNOTATION_PATH, max_images_per_emotion)
        EMOSET_CENTROIDS = calculate_centroids(dataset)
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
