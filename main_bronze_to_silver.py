from app.core.config import Config
from app.infrastructure.minio_adapter import MinioAdapter
from app.use_cases.bronze_to_silver import BronzeToSilverService

def main():
    # 1. Створюємо інструменти (Infrastructure)
    minio_adapter = MinioAdapter(
        endpoint=Config.MINIO_ENDPOINT,
        access_key=Config.MINIO_ACCESS_KEY,
        secret_key=Config.MINIO_SECRET_KEY,
        secure=Config.MINIO_SECURE
    )

    # 2. Створюємо сценарій (Use Case) і передаємо йому інструменти
    service = BronzeToSilverService(minio_adapter)

    # 3. Запускаємо виконання
    service.execute(
        local_path='data/bronze/amazon_reviews.csv', 
        bucket_name="silver", 
        object_name="reviews.parquet"
    )

if __name__ == "__main__":
    main()