from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request, Depends
from fastapi.responses import JSONResponse, Response
import uuid
import requests
from sqlalchemy.orm import Session
import os

from database import SessionLocal, engine
import db_models
from db_models import MusicRequest

# Создаем таблицы, если их ещё нет
db_models.Base.metadata.create_all(bind=engine)

from image_analysis import analyze_image
from text_generation import generate_concise_music_prompt_from_analysis

app = FastAPI()

# Добавляем CORS (при необходимости)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно указать конкретные адреса
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUNO_API_URL = "https://apibox.erweima.ai/api/v1/generate"  # Если у вас Suno API внешний, оставьте как было
# Здесь SUNO_TOKEN можно оставить, если он используется для вызова внешнего API.
SUNO_TOKEN = os.environ.get("SUNO_TOKEN", "d79b625c9afddded7e8bbaf2e99ed05a")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_music_with_suno(prompt: str, style: str, title: str, instrumental: bool, negative_tags: str) -> dict:
    payload = {
        "prompt": prompt,
        "style": style,
        "title": title,
        "customMode": True,
        "instrumental": instrumental,
        "model": "V3_5",
        "negativeTags": negative_tags,
        # Для публичного доступа используйте внешний адрес, например через ngrok
        "callBackUrl": "https://flamingo-key-owl.ngrok-free.app/api/webhook"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {SUNO_TOKEN}"
    }
    resp = requests.post(SUNO_API_URL, json=payload, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    raise Exception("Error generating music from Suno API")

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Загружает изображение, выполняет анализ, генерирует промпт и сохраняет файл на диск.
    Запись сохраняется со статусом 'uploaded'. В ответ возвращается request_id, промпт и результаты анализа.
    """
    try:
        contents = await file.read()
        analysis_result = analyze_image(contents)
        prompt = generate_concise_music_prompt_from_analysis(
            analysis_result["emotion"],
            analysis_result["brightness"],
            analysis_result["colorfulness"],
            analysis_result.get("face_count"),
            analysis_result.get("objects")
        )
        req_id = str(uuid.uuid4())
        
        # Сохраняем файл в директорию "uploads"
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        file_path = os.path.join(upload_dir, req_id + ext)
        with open(file_path, "wb") as f:
            f.write(contents)
        
        new_request = MusicRequest(
            id=req_id,
            prompt=prompt,
            status="uploaded",
            image_path=file_path,
            style="",
            title="",
            instrumental=True,
            negative_tags=""
        )
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        return JSONResponse({
            "request_id": req_id,
            "prompt": prompt,
            "analysis": analysis_result
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-music")
async def generate_music(
    request_id: str = Form(...),
    style: str = Form(...),
    title: str = Form(...),
    instrumental: bool = Form(True),
    negative_tags: str = Form(""),
    db: Session = Depends(get_db)
):
    req = db.query(MusicRequest).filter(MusicRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    # Обновляем параметры генерации
    req.style = style
    req.title = title
    req.instrumental = instrumental
    req.negative_tags = negative_tags
    req.status = "music_requested"
    db.commit()
    db.refresh(req)

    # Вызываем Suno API
    suno_response = generate_music_with_suno(req.prompt, style, title, instrumental, negative_tags)

    # Сохраняем taskId (именно в этом поле Suno отдаёт taskId)
    task_id = suno_response.get("data", {}).get("taskId")
    if task_id:
        req.suno_task_id = task_id
        db.commit()
        db.refresh(req)

    return JSONResponse(suno_response)

@app.get("/api/queries")
def get_queries(db: Session = Depends(get_db)):
    requests_list = db.query(MusicRequest).order_by(MusicRequest.created_at.desc()).all()
    # Чтобы избежать проблем с сериализацией, не возвращаем поле image_path raw (оно передается как строка)
    results = []
    for req in requests_list:
        results.append({
            "id": req.id,
            "prompt": req.prompt,
            "style": req.style,
            "title": req.title,
            "instrumental": req.instrumental,
            "negative_tags": req.negative_tags,
            "suno_task_id": req.suno_task_id,
            "music_details": req.music_details,
            "status": req.status,
            "created_at": req.created_at.isoformat(),
            "image_path": req.image_path  # Можно использовать для формирования URL на фронте
        })
    return JSONResponse(results)

@app.get("/api/queries/{request_id}")
def get_query_details(request_id: str, db: Session = Depends(get_db)):
    req = db.query(MusicRequest).filter(MusicRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    result = {
        "id": req.id,
        "prompt": req.prompt,
        "style": req.style,
        "title": req.title,
        "instrumental": req.instrumental,
        "negative_tags": req.negative_tags,
        "suno_task_id": req.suno_task_id,
        "music_details": req.music_details,
        "status": req.status,
        "created_at": req.created_at.isoformat(),
        "image_path": req.image_path
    }
    return JSONResponse(result)

@app.get("/api/image/{request_id}")
def get_image(request_id: str, db: Session = Depends(get_db)):
    req = db.query(MusicRequest).filter(MusicRequest.id == request_id).first()
    if req and req.image_path and os.path.exists(req.image_path):
        ext = os.path.splitext(req.image_path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            media_type = "image/jpeg"
        elif ext == ".png":
            media_type = "image/png"
        else:
            media_type = "application/octet-stream"
        with open(req.image_path, "rb") as f:
            image_bytes = f.read()
        return Response(content=image_bytes, media_type=media_type)
    raise HTTPException(status_code=404, detail="Image not found")

@app.get("/api/analytics")
def get_analytics(db: Session = Depends(get_db)):
    total = db.query(MusicRequest).count()
    return JSONResponse({"total_requests": total})

@app.post("/api/webhook")
async def webhook_handler(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    data = payload.get("data", {})
    task_id = data.get("task_id")
    if not task_id:
        raise HTTPException(status_code=400, detail="No task_id in webhook data")

    req = db.query(MusicRequest).filter(MusicRequest.suno_task_id == task_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found for this task_id")

    # Сохраняем массив сгенерированных треков
    req.music_details = data.get("data")
    req.status = "music_generated"
    db.commit()
    db.refresh(req)
    return JSONResponse({"status": "received"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
