from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from database import Base

class MusicRequest(Base):
    __tablename__ = "music_requests"
    id = Column(String, primary_key=True, index=True)  # request_id
    prompt = Column(Text, nullable=False)
    style = Column(String, nullable=True)
    title = Column(String, nullable=True)
    instrumental = Column(Boolean, default=True)
    negative_tags = Column(String, default="")
    suno_task_id = Column(String, nullable=True)
    music_details = Column(JSON, nullable=True)
    status = Column(String, default="uploaded")  # uploaded, music_requested, music_generated, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    image_path = Column(String, nullable=True)  # Сохраняем путь к изображению
    analysis_result = Column(JSON, nullable=True)  # emotion/brightness/colorfulness/face_count/objects из /api/upload