from app.core.config import Config
from app.infrastructure.spark_manager import SparkManager
from app.use_cases.silver_to_gold import SilverToGoldService

def main():
    print("🚀 Запуск процесу Silver to Gold...")

    # 1. Отримуємо Spark Session через наш менеджер
    spark = SparkManager.get_session("SilverToGoldApp", Config)

    # 2. Ініціалізуємо сервіс
    service = SilverToGoldService(spark)

    try:
        # 3. Виконуємо обробку
        # Шлях s3a:// вже налаштований у SparkManager
        service.execute("s3a://silver/reviews.parquet")
    finally:
        # Важливо завжди зупиняти сесію
        spark.stop()
        print("🛑 Spark Session зупинено.")

if __name__ == "__main__":
    main()