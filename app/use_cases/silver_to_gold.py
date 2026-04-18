"""
Silver to Gold transformation.
- 3 types of aggregations (Product stats, Customer activity, Monthly trends).
- Saving to 3 separate MongoDB collections.
"""

import structlog
import time
from pyspark.sql import functions as F
from app.core.exceptions import TransformationError, StorageError

logger = structlog.get_logger()

class SilverToGoldService:
    def __init__(self, spark_session, mongodb_adapter):
        self.spark = spark_session
        self.mongodb = mongodb_adapter

    def execute(self, input_path: str, output_path: str = None):
        try:
            logger.info("silver_to_gold_start", input_path=input_path)

            # 1. Читаємо дані з Silver шару (MinIO)
            df = self.spark.read.parquet(input_path)
            
            # 2. Очищення (згідно з ТЗ: видаляємо NULL у критичних колонках)
            df_clean = df.filter(
                (F.col("review_id").isNotNull()) &
                (F.col("product_id").isNotNull()) &
                (F.col("star_rating").isNotNull()) &
                (F.col("review_date").isNotNull())
            )

            # ---------------------------------------------------------
            # 3. АГРЕГАЦІЇ (3 ТИПИ ЗГІДНО З ЗАВДАННЯМ)
            # ---------------------------------------------------------

            # Агрегація 1: Статистика по продуктах (Рейтинг + Кількість)
            df_product_stats = df_clean.groupBy("product_id").agg(
                F.round(F.avg("star_rating"), 2).alias("avg_rating"),
                F.count("review_id").alias("total_reviews")
            )

            # Агрегація 2: Активність клієнтів (Тільки верифіковані покупки)
            df_customer_activity = df_clean.filter(F.col("verified_purchase") == 1) \
                .groupBy("customer_id") \
                .agg(F.count("review_id").alias("verified_reviews_count"))

            # Агрегація 3: Щомісячні тренди (Кількість відгуків по місяцях)
            df_monthly_trends = df_clean.withColumn("month", F.month("review_date")) \
                .withColumn("year", F.year("review_date")) \
                .groupBy("product_id", "year", "month") \
                .agg(F.count("review_id").alias("reviews_count"))

            # ---------------------------------------------------------
            # 4. ЗБЕРЕЖЕННЯ В MONGODB (У 3 РІЗНІ КОЛЕКЦІЇ)
            # ---------------------------------------------------------
            
            # Запис 1: Продукти
            self._save_to_mongodb(df_product_stats, "product_stats", "product_id")
            
            # Запис 2: Клієнти
            self._save_to_mongodb(df_customer_activity, "customer_activity", "customer_id")
            
            # Запис 3: Тренди (тут ключ композитний, тому просто вставляємо)
            self._save_to_mongodb(df_monthly_trends, "product_monthly_trends", None)

            # 5. Збереження в MinIO (опціонально, як бекап аналітики)
            if output_path:
                df_product_stats.write.mode("overwrite").parquet(output_path)

            # ---------------------------------------------------------
            # 6. ПАУЗА ДЛЯ PROMETHEUS (ЩОБ ВСТИГ ЗАБРАТИ МЕТРИКИ)
            # ---------------------------------------------------------
            logger.info("waiting_for_prometheus_scraping", seconds=30)
            time.sleep(30)

            logger.info("silver_to_gold_complete")
            return df_product_stats

        except Exception as e:
            logger.error("silver_to_gold_failed", error=str(e))
            raise TransformationError(f"Silver to Gold failed: {e}")

    def _save_to_mongodb(self, df, collection_name, key_field):
        """Внутрішній метод для конвертації та запису в Mongo."""
        try:
            records = [row.asDict() for row in df.collect()]
            if not records:
                return

            if key_field:
                # Робимо Upsert, щоб не дублювати дані при повторних запусках
                self.mongodb.bulk_upsert(
                    collection=collection_name,
                    documents=records,
                    key_field=key_field
                )
            else:
                # Для трендів просто вставляємо (або можна налаштувати інший ключ)
                self.mongodb.insert_many(collection_name, records)
                
            logger.info("mongodb_save_success", collection=collection_name, count=len(records))
        except Exception as e:
            logger.error("mongodb_save_error", collection=collection_name, error=str(e))