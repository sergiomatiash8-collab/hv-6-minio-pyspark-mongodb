"""
Main entry point for Silver to Gold transformation.
FIXES: Proper logging, MongoDB integration, metrics.
"""

import time
import structlog
from prometheus_client import start_http_server, Counter, Histogram

from app.core.config import Config
from app.infrastructure.spark_manager import SparkManager
from app.infrastructure.mongodb_adapter import MongoDBAdapter
# Оцей рядок ми виправили:
from app.infrastructure.logging_config import configure_logging 
from app.use_cases.silver_to_gold import SilverToGoldService

# Далі решта коду...

# Configure logging
logger = configure_logging("INFO")

# Metrics
JOB_COUNTER = Counter(
    'etl_jobs_total', 
    'Total ETL jobs', 
    ['layer', 'status']
)
JOB_DURATION = Histogram(
    'etl_job_duration_seconds', 
    'ETL job duration', 
    ['layer']
)

def main():
    logger.info("silver_to_gold_job_start")
    start_time = time.time()

    # Start Prometheus metrics server (доступний на http://localhost:8000)
    try:
        start_http_server(8000)
        logger.info("metrics_server_started", port=8000)
    except Exception as e:
        logger.warning("metrics_server_failed", error=str(e))

    spark = None
    mongodb = None

    try:
        # 1. Initialize Spark
        spark = SparkManager.get_session("SilverToGoldApp", Config)

        # 2. Initialize MongoDB
        mongodb = MongoDBAdapter(
            connection_string=Config.MONGO_URL,
            database="amazon_reviews"
        )

        # 3. Initialize service
        service = SilverToGoldService(spark, mongodb)

        # 4. Execute transformation
        service.execute(
            # Вказуємо ту саму назву, яку ми створили в попередньому скрипті
            input_path="s3a://silver/amazon_reviews.parquet", 
            output_path="s3a://gold/product_analytics.parquet"
        )

        # Success metrics
        duration = time.time() - start_time
        JOB_COUNTER.labels(layer='silver_to_gold', status='success').inc()
        JOB_DURATION.labels(layer='silver_to_gold').observe(duration)

        logger.info("silver_to_gold_job_complete", duration_seconds=round(duration, 2))

    except Exception as e:
        duration = time.time() - start_time
        JOB_COUNTER.labels(layer='silver_to_gold', status='failed').inc()
        JOB_DURATION.labels(layer='silver_to_gold').observe(duration)
        
        logger.error("silver_to_gold_job_failed", 
                     error=str(e), 
                     duration_seconds=round(duration, 2))
        raise

    finally:
        # Cleanup - важливо для Docker, щоб не "вішали" сесії
        if mongodb:
            mongodb.close()
        if spark:
            spark.stop()
            logger.info("spark_session_stopped")
        
        # Даємо трохи часу метрикам "пролетіти", якщо скрипт працює в циклі
        time.sleep(2)

if __name__ == "__main__":
    main()