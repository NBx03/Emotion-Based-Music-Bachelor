from database import SessionLocal
from db_models import MusicRequest

def clear_all():
    db = SessionLocal()
    try:
        # Удалить ВСЕ записи
        # db.query(MusicRequest).delete()
        # Или, например, только с status='uploaded':
        db.query(MusicRequest).filter(MusicRequest.status == 'uploaded').delete()

        db.commit()
        print("DB очищена")
    finally:
        db.close()

if __name__ == "__main__":
    clear_all()
