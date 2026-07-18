# backend/data/

`emoset_centroids.json` — предподсчитанные центроиды эмоций (усреднённые
CLIP-эмбеддинги по каждому классу EmoSet). Backend грузит этот файл при
старте (`image_analysis.load_emoset`) вместо того, чтобы пересчитывать
центроиды из полного датасета EmoSet при каждом запуске.

Файл не входит в этот коммит — сгенерируйте его самостоятельно там, где
физически лежит датасет EmoSet:

```bash
python scripts/precompute_centroids.py \
    --image-path D:/EmoSet/image \
    --annotation-path D:/EmoSet/annotation \
    --output backend/data/emoset_centroids.json
```

После генерации закоммитьте получившийся `emoset_centroids.json` — тогда
обычный запуск backend'а больше не требует доступа к датасету.
