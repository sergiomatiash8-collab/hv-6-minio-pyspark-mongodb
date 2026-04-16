import sys
from app.core.config import Config
from app.infrastructure.minio_adapter import MinioAdapter
from app.use_cases.bronze_to_silver import BronzeToSilverService

def main():
    try:
        print(">>> ЗАПУСК ПРОЦЕСУ: BRONZE TO SILVER <<<")

        # 1. Ініціалізація інфраструктури
        minio_adapter = MinioAdapter(
            endpoint=Config.MINIO_ENDPOINT,
            access_key=Config.MINIO_ACCESS_KEY,
            secret_key=Config.MINIO_SECRET_KEY,
            secure=Config.MINIO_SECURE
        )

        # 2. Створення сервісу
        service = BronzeToSilverService(minio_adapter)

        # 3. Виконання
        service.execute(
            local_path='data/bronze/amazon_reviews.csv', 
            bucket_name="silver", 
            object_name="reviews.parquet"
        )
        
        print(">>> ПРОЦЕС ЗАВЕРШЕНО УСПІШНО! <<<")

    except ConnectionError as e:
        print(f"[КРИТИЧНА ПОМИЛКА МЕРЕЖІ]: Не вдалося підключитися до MinIO. Перевір, чи запущено Docker-контейнер. \nДеталі: {e}")
        sys.exit(1)
        
    except FileNotFoundError as e:
        print(f"[ПОМИЛКА ДАНИХ]: Файл не знайдено за вказаним шляхом. \nДеталі: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"[НЕПЕРЕДБАЧУВАНА ПОМИЛКА]: Сталося щось дивне... \nТип помилки: {type(e).__name__} \nОпис: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()