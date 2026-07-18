from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "")
# Удаляем BOM, если он там есть
if DATABASE_URL.startswith("\ufeff"):
    DATABASE_URL = DATABASE_URL.lstrip("\ufeff")
DATABASE_URL = DATABASE_URL.replace(r"\x3a", ":")

# По умолчанию используем локальный SQLite — Postgres подключается явно через DATABASE_URL
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./app.db"

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {"options": "-c client_encoding=utf8"}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
