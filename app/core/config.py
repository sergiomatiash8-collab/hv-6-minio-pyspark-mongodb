import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MinIO settings
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

    # Spark settings
    SPARK_APP_NAME = "AmazonReviewsETL"
    
    # MongoDB settings
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://admin:password@mongodb:27017")