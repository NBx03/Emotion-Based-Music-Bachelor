def build_segment_data(emotion, brightness, colorfulness, face_count=None, objects=None):
    """
    Формирует список сегментов с приоритетом и двумя вариантами: long и short.
    Если людей или объектов не обнаружено, соответствующий сегмент не добавляется.
    Приоритеты:
      1) вступительная фраза,
      2) эмоция,
      3) яркость,
      4) цвета,
      5) лица (если обнаружены),
      6) объекты (если обнаружены).
    """
    emotion_map_long = {
        "amusement": "a joyful and uplifting scene, full of light-heartedness and cheer.",
        "anger": "a tense and angry atmosphere, filled with frustration and intensity.",
        "awe": "a breathtaking moment, filled with wonder and admiration.",
        "contentment": "a peaceful and calm setting, evoking satisfaction and harmony.",
        "disgust": "an unpleasant and unsettling environment, causing discomfort and repulsion.",
        "excitement": "a thrilling and energetic scene, full of anticipation and adrenaline.",
        "fear": "a fearful and eerie atmosphere, filled with uncertainty and dread.",
        "sadness": "a somber and melancholic moment, evoking a deep sense of sadness."
    }
    emotion_long = emotion_map_long.get(emotion, "a scene with ambiguous emotions.")
    emotion_short = emotion if emotion else "ambiguous mood"

    if brightness > 0.7:
        bright_long = "The scene is brightly lit, bathed in intense light."
        bright_short = "Brightly lit scene."
    elif brightness > 0.4:
        bright_long = "The scene is moderately lit, with balanced lighting and shadow."
        bright_short = "Moderately lit scene."
    else:
        bright_long = "The scene is dark and moody, with deep shadows and minimal light."
        bright_short = "Dark, moody scene."

    if colorfulness > 0.7:
        color_long = "The colors are rich and saturated, creating a vivid and dynamic feel."
        color_short = "Rich, saturated colors."
    elif colorfulness > 0.4:
        color_long = "The colors are somewhat muted but balanced, creating a soft and neutral tone."
        color_short = "Muted but balanced colors."
    else:
        color_long = "The colors are subdued and minimal, enhancing the somber and quiet mood."
        color_short = "Subdued, minimal colors."

    segments = [
        {
            "priority": 1,
            "long": "Compose music for scene:",
            "short": "Compose music for scene:"
        },
        {
            "priority": 2,
            "long": emotion_long,
            "short": emotion_short
        },
        {
            "priority": 3,
            "long": bright_long,
            "short": bright_short
        },
        {
            "priority": 4,
            "long": color_long,
            "short": color_short
        }
    ]

    # Добавляем сегмент о людях, только если обнаружены лица
    if face_count is not None and face_count > 0:
        if face_count == 1:
            face_long = "There is 1 person present, reflecting the scene's mood."
            face_short = "1 person present."
        else:
            face_long = f"There are {face_count} people, reflecting the scene's overall mood."
            face_short = f"{face_count} people present."
        segments.append({
            "priority": 5,
            "long": face_long,
            "short": face_short
        })

    # Добавляем сегмент об объектах, только если объекты обнаружены
    if objects:
        joined_objects = ", ".join(objects[:3])
        if len(objects) > 3:
            joined_objects += "..."
        obj_long = f"The scene includes notable objects such as: {joined_objects}."
        obj_short = f"Objects: {joined_objects}."
        segments.append({
            "priority": 6,
            "long": obj_long,
            "short": obj_short
        })

    return segments

def generate_concise_music_prompt_from_analysis(
    emotion, brightness, colorfulness, face_count=None, objects=None, max_length=199
):
    """
    Сначала формирует базовый итоговый текст, используя короткие версии всех сегментов,
    а затем по приоритету пытается заменить короткие версии на длинные,
    если итоговый текст всё ещё укладывается в max_length символов.
    """
    segments = build_segment_data(emotion, brightness, colorfulness, face_count, objects)
    # Сортируем по приоритету
    segments.sort(key=lambda s: s["priority"])
    
    # Сначала составляем базовый текст из short версий всех сегментов
    current_versions = {seg["priority"]: seg["short"] for seg in segments}
    
    def build_text(versions):
        texts = [versions[seg["priority"]] for seg in segments]
        return " ".join(texts)
    
    final_text = build_text(current_versions)
    if len(final_text) > max_length:
        # Если даже короткие версии не укладываются (маловероятно), обрезаем жестко
        return final_text[:max_length]
    
    # Пытаемся по порядку улучшить описание, заменяя short на long версии,
    # если итоговый текст остаётся в пределах max_length
    for seg in segments:
        temp_versions = current_versions.copy()
        temp_versions[seg["priority"]] = seg["long"]
        candidate = build_text(temp_versions)
        if len(candidate) <= max_length:
            current_versions = temp_versions  # обновляем, если кандидат влезает
    
    final_text = build_text(current_versions)
    return final_text if len(final_text) <= max_length else final_text[:max_length]