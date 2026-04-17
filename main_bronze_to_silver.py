import os
from app.core.config import Config
from app.infrastructure.minio_adapter import MinioAdapter
from app.use_cases.bronze_to_silver import BronzeToSilverService

def main():
    # 1. Підключаємось до MinIO
    adapter = MinioAdapter(
        endpoint=Config.MINIO_ENDPOINT,
        access_key=Config.MINIO_ACCESS_KEY,
        secret_key=Config.MINIO_SECRET_KEY,
        secure=Config.MINIO_SECURE
    )

    service = BronzeToSilverService(adapter)

    # 2. Шлях саме до твого файлу (згідно зі скріншотом)
    local_file = "data/bronze/amazon_reviews.csv" 
    
    if not os.path.exists(local_file):
        print(f"❌ Помилка: Не бачу файл за шляхом {local_file}")
        print("Перевір, чи ти запустив термінал саме в папці проєкту.")
        return

    try:
        print(f"🚀 Читаємо CSV: {local_file}...")
        
        # Виконуємо трансформацію та завантаження
        service.execute(
            local_path=local_file,
            bucket_name="silver",
            object_name="amazon_reviews.parquet"
        )
        
        print("✅ Успішно! Parquet вже лежить у MinIO (бакет 'silver').")

    except Exception as e:
        print(f"💥 Помилка: {e}")

if __name__ == "__main__":
    main()