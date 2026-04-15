class SilverToGoldService:
    def __init__(self, spark_session):
        # Отримуємо вже налаштовану сесію Spark
        self.spark = spark_session

    def execute(self, input_path: str):
        print(f"🔄 Починаю обробку Silver шару з: {input_path}")

        # 1. Читаємо Parquet прямо з MinIO
        df = self.spark.read.parquet(input_path)

        # 2. Очистка (базова фільтрація)
        # В ідеалі ми винесемо це в Core наступним кроком
        df_clean = df.filter(
            (df.review_id.isNotNull()) &
            (df.product_id.isNotNull()) &
            (df.star_rating.isNotNull()) &
            (df.review_date.isNotNull())
        )

        print(f"📊 Дані зчитано. Кількість рядків після очистки: {df_clean.count()}")
        
        # Повертаємо очищений DataFrame для подальших агрегацій
        return df_clean