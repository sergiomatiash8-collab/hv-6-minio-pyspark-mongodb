"""
Silver to Gold transformation with proper output and error handling.
FIXES: Now actually saves results to MongoDB and MinIO!
"""

import structlog
from pyspark.sql import functions as F
from app.core.exceptions import TransformationError, StorageError

logger = structlog.get_logger()

class SilverToGoldService:
    def __init__(self, spark_session, mongodb_adapter):
        self.spark = spark_session
        self.mongodb = mongodb_adapter

    def execute(self, input_path: str, output_path: str = None):
        """
        Transform Silver to Gold layer.
        """
        try:
            logger.info("silver_to_gold_start", input_path=input_path)

            # 1. Read from Silver
            df = self.spark.read.parquet(input_path)
            initial_count = df.count()
            
            logger.info("silver_data_loaded", 
                        path=input_path, 
                        row_count=initial_count)

            # 2. Data quality checks
            if initial_count == 0:
                raise TransformationError("Input data is empty")

            # 3. Clean data (ensure no NULLs in keys)
            df_clean = df.filter(
                (F.col("review_id").isNotNull()) &
                (F.col("product_id").isNotNull()) &
                (F.col("star_rating").isNotNull()) &
                (F.col("review_date").isNotNull())
            )

            clean_count = df_clean.count()
            rejected_count = initial_count - clean_count
            
            if initial_count > 0:
                rejection_rate = rejected_count / initial_count
                logger.info("data_cleaning_complete", 
                            clean_rows=clean_count, 
                            rejected_rows=rejected_count, 
                            rejection_rate=f"{rejection_rate:.2%}")

            # 4. Aggregate to Gold layer
            df_gold = df_clean.groupBy("product_id").agg(
                F.round(F.avg("star_rating"), 2).alias("avg_rating"),
                F.count("review_id").alias("total_reviews"),
                F.sum(
                    F.when(F.col("verified_purchase") == True, 1).otherwise(0)
                ).alias("verified_reviews"),
                F.max("review_date").alias("last_review_date")
            )

            gold_count = df_gold.count()
            logger.info("aggregation_complete", products=gold_count)

            # 5. Save to MinIO (Analytical storage)
            if output_path:
                df_gold.write.mode("overwrite").parquet(output_path)
                logger.info("gold_data_saved_minio", path=output_path)

            # 6. Save to MongoDB (Operational storage / API source)
            self._save_to_mongodb(df_gold)

            logger.info("silver_to_gold_complete", products_processed=gold_count)
            return df_gold

        except Exception as e:
            logger.error("silver_to_gold_failed", error=str(e))
            raise TransformationError(f"Silver to Gold failed: {e}")

    def _save_to_mongodb(self, df_gold):
        """Save aggregated data to MongoDB."""
        try:
            # Конвертуємо у список словників для MongoDB
            # Примітка: для дуже великих об'ємів краще використовувати spark-mongodb connector,
            # але для агрегованого Gold шару collect() зазвичай достатньо.
            records = [row.asDict() for row in df_gold.collect()]
            
            if not records:
                logger.warning("mongodb_save_skip", reason="No records to save")
                return

            # Використовуємо наш адаптер для Bulk Upsert
            self.mongodb.bulk_upsert(
                collection="product_reviews_gold",
                documents=records,
                key_field="product_id"
            )
            
            logger.info("mongodb_save_complete", records_count=len(records))
        except Exception as e:
            logger.error("mongodb_save_failed", error=str(e))
            raise StorageError(f"Failed to save to MongoDB: {e}")