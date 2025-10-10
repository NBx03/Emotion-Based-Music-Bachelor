import os, json
from PIL import Image, ImageStat
import numpy as np
import torch
import torchvision.transforms as transforms
from transformers import CLIPProcessor, CLIPModel
import face_recognition
import requests
import pandas as pd

session = requests.Session()
session.verify = False

# Инициализируем модель CLIP
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", use_auth_token=False, trust_remote_code=True)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Загружаем модель YOLOv5 для распознавания объектов
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def get_image_embedding(image_path):
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    outputs = model.get_image_features(**inputs)
    return outputs.detach().numpy().flatten()

def load_dataset(dataset_image_path, dataset_annotation_path, max_images_per_emotion=100):
    dataset = []
    for emotion in os.listdir(dataset_image_path):
        emotion_image_path = os.path.join(dataset_image_path, emotion)
        emotion_annotation_path = os.path.join(dataset_annotation_path, emotion)
        if os.path.isdir(emotion_image_path) and os.path.isdir(emotion_annotation_path):
            images_processed = 0
            for image_name in os.listdir(emotion_image_path):
                if image_name.lower().endswith(('.jpg', '.png')):
                    image_path = os.path.join(emotion_image_path, image_name)
                    annotation_path = os.path.join(emotion_annotation_path, image_name.rsplit('.', 1)[0] + '.json')
                    if os.path.exists(annotation_path):
                        with open(annotation_path, 'r') as f:
                            annotation = json.load(f)
                        embedding = get_image_embedding(image_path)
                        dataset.append((embedding, annotation))
                        images_processed += 1
                        if images_processed >= max_images_per_emotion:
                            break
    return dataset

def calculate_centroids(dataset):
    emotion_clusters = {}
    for embedding, annotation in dataset:
        emotion = annotation['emotion']
        if emotion not in emotion_clusters:
            emotion_clusters[emotion] = []
        emotion_clusters[emotion].append(embedding)
    centroids = {}
    for emotion, embeddings in emotion_clusters.items():
        centroids[emotion] = np.mean(embeddings, axis=0)
    return centroids

def calculate_brightness(image_path):
    image = Image.open(image_path).convert('L')
    stat = ImageStat.Stat(image)
    return stat.mean[0] / 255.0

def calculate_colorfulness(image_path):
    image = Image.open(image_path)
    stat = ImageStat.Stat(image)
    r, g, b = stat.mean[:3]
    return (max(r, g, b) - min(r, g, b)) / 255.0

def detect_objects(image_path, confidence_threshold=0.5):
    results = yolo_model(image_path)
    detected_objects = results.pandas().xyxy[0]
    filtered_objects = detected_objects[detected_objects['confidence'] >= confidence_threshold]
    object_names = filtered_objects['name'].tolist()
    if not object_names:
        return None
    return object_names

def detect_faces(image_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    return len(face_locations)

def determine_emotion(image_path, centroids):
    image_embedding = get_image_embedding(image_path)
    from scipy.spatial.distance import cosine
    similarities = []
    for emotion, centroid in centroids.items():
        similarity = cosine(image_embedding, centroid)
        similarities.append((similarity, emotion))
    best_match = min(similarities, key=lambda x: x[0])
    return best_match[1]
