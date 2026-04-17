import os
from dotenv import load_dotenv

# Завантажуємо змінні з .env файлу
load_dotenv()

class Config:
    # MinIO налаштування (беремо назви точно як у твоєму .env)
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

    # MongoDB налаштування (якщо знадобляться для Silver -> Gold)
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "etl_database")