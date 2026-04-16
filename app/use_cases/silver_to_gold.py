class SilverToGoldService:
    def __init__(self, spark_session):
        self.spark = spark_session

    def execute(self, input_path: str):
        print(f"🔄 Починаю обробку Silver шару (Direct S3) з: {input_path}")

        # Spark сам піде в MinIO через налаштований s3a
        df = self.spark.read.parquet(input_path)

        df_clean = df.filter(
            (df.review_id.isNotNull()) &
            (df.product_id.isNotNull()) &
            (df.star_rating.isNotNull()) &
            (df.review_date.isNotNull())
        )

        print(f"📊 Дані оброблено. Кількість рядків: {df_clean.count()}")
        return df_clean