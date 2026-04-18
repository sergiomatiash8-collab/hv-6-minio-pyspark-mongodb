import structlog
import time
from pyspark.sql import functions as F
from app.core.exceptions import TransformationError

logger = structlog.get_logger()

class SilverToGoldService:
    def __init__(self, spark_session, mongodb_adapter):
        self.spark = spark_session
        self.mongodb = mongodb_adapter

    def execute(self, input_path: str, output_path: str = None):
        try:
            logger.info("silver_to_gold_start", input_path=input_path)

            
            df = self.spark.read.parquet(input_path)
            
            
            df_clean = df.filter(
                (F.col("review_id").isNotNull()) &
                (F.col("product_id").isNotNull()) &
                (F.col("star_rating").isNotNull()) &
                (F.col("review_date").isNotNull())
            ).cache()

           
            df_product_stats = df_clean.groupBy("product_id").agg(
                F.round(F.avg("star_rating"), 2).alias("avg_rating"),
                F.count("review_id").alias("total_reviews")
            )

            
            df_customer_activity = df_clean.filter(
                (F.col("verified_purchase").cast("string") == "Y") | 
                (F.col("verified_purchase").cast("string") == "1") |
                (F.col("verified_purchase").cast("string") == "true")
            ).groupBy("customer_id").agg(F.count("review_id").alias("verified_reviews_count"))

            
            df_monthly_trends = df_clean.withColumn("month", F.month("review_date")) \
                .withColumn("year", F.year("review_date")) \
                .groupBy("product_id", "year", "month") \
                .agg(F.count("review_id").alias("reviews_count"))

            
            
            logger.info("saving_to_mongodb_started")
            
            
            self._save_to_mongodb(df_product_stats, "product_stats", "product_id")
            
            
            self._save_to_mongodb(df_customer_activity, "customer_activity", "customer_id")
            
            
            self._save_to_mongodb(df_monthly_trends, "product_monthly_trends", None)

            if output_path:
                df_product_stats.write.mode("overwrite").parquet(output_path)

            df_clean.unpersist()
            logger.info("silver_to_gold_complete")
            return df_product_stats

        except Exception as e:
            logger.error("silver_to_gold_failed", error=str(e))
            raise TransformationError(f"Silver to Gold failed: {e}")

    def _save_to_mongodb(self, df, collection_name, key_field):
        try:
            logger.info("batch_save_start", collection=collection_name)
            iterator = df.toLocalIterator()
            batch = []
            batch_size = 5000 
            total_count = 0

            for row in iterator:
                batch.append(row.asDict())
                if len(batch) >= batch_size:
                    self._process_batch(batch, collection_name, key_field)
                    total_count += len(batch)
                    batch = []

            if batch:
                self._process_batch(batch, collection_name, key_field)
                total_count += len(batch)

            if total_count == 0:
                logger.warning("mongodb_save_empty", collection=collection_name)
            else:
                logger.info("mongodb_full_save_success", collection=collection_name, total_records=total_count)
        except Exception as e:
            logger.error("mongodb_save_error", collection=collection_name, error=str(e))
            raise

    def _process_batch(self, batch, collection_name, key_field):
        if key_field:
            self.mongodb.bulk_upsert(collection=collection_name, documents=batch, key_field=key_field)
        else:
            self.mongodb.insert_many(collection_name, batch)